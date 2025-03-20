# -*- coding: cp949 -*-
import socket
import select
import random

def refresh_temp(curr_temp):
    """현재 온도를 -1, 0, 1 범위로 무작위 변경"""
    return curr_temp + random.randint(-1, 1)

def coordinator():
    server_address = ('127.0.0.1', 8080)
    
    # TCP/IP 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(5)

    # select 함수용 소켓 목록
    sockets_list = [server_socket]
    print("Coordinator가 {}:{}에서 대기 중입니다.".format(*server_address))

    # 초기 설정 값
    upper_bound = 30     # Upper Bound (최대 온도)
    lower_bound = -5     # Lower Bound (최소 온도)
    current_temp = 25    # Current Temperature (현재 온도)

    while True:
        # 들어오는 연결 또는 데이터를 대기
        read_sockets, _, _ = select.select(sockets_list, [], [])
        
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                # 새로운 연결 수락
                client_socket, client_address = server_socket.accept()
                sockets_list.append(client_socket)
                print(f"새로운 연결을 수락했습니다: {client_address}")
            else:
                # 클라이언트로부터 메시지 수신
                data = notified_socket.recv(1024)
                if data:
                    message = data.decode()
                    print(f"{notified_socket.getpeername()}로부터 메시지를 수신했습니다: {message}")
                    
                    # CONFIGURE 명령어 처리
                    if message.startswith("CONFIGURE"):
                        parts = message.split()
                        if len(parts) == 3:
                            command_type = parts[1].lower()
                            try:
                                value = int(parts[2])
                                if command_type == "lower_bound":
                                    lower_bound = value
                                    response = f"Lower bound가 {lower_bound}도로 설정되었습니다."
                                elif command_type == "upper_bound":
                                    upper_bound = value
                                    response = f"Upper bound가 {upper_bound}도로 설정되었습니다."
                                else:
                                    response = "잘못된 설정 유형입니다. 'upper_bound' 또는 'lower_bound'만 설정 가능합니다."
                                notified_socket.send(response.encode())
                            except ValueError:
                                notified_socket.send("잘못된 값입니다. 정수를 입력하세요.".encode())
                        else:
                            notified_socket.send("잘못된 명령어 형식입니다. 'CONFIGURE <lower_bound|upper_bound> <값>' 형식으로 입력하세요.".encode())

                    # QUERY 명령어 처리
                    elif message.lower() == "query":
                        status = f"Current temperature: {current_temp}, Lower bound: {lower_bound}, Upper bound: {upper_bound}"
                        notified_socket.send(status.encode())

                    # POLLING 명령어 처리
                    elif message.lower() == "polling":
                        # 현재 온도 확인 및 상태 결정
                        if lower_bound <= current_temp <= upper_bound:
                            status = "safe"
                        else:
                            status = "warning"
                        notified_socket.send(f"Current temperature: {current_temp}, Status: {status}".encode())

                else:
                    # 연결이 종료됨
                    print(f"{notified_socket.getpeername()}와의 연결이 종료되었습니다.")
                    sockets_list.remove(notified_socket)
                    notified_socket.close()

if __name__ == "__main__":
    coordinator()
