# -*- coding: cp949 -*-
import socket
import time

# Commander 기능 구현
def commander(sock):
    try:
        print("Commander가 Coordinator에 연결되었습니다. 'QUERY', 'CONFIGURE UPPER_BOUND <값>', 'CONFIGURE LOWER_BOUND <값>' 명령어를 사용해 보일러 설정을 조정하세요.")
        while True:
            # 사용자 입력을 받아 서버로 전송
            message = input("Commander: ")
            if message.lower() == 'exit':
                break
            sock.sendall(message.encode())
            # 서버로부터 응답 수신
            data = sock.recv(1024)
            if data:
                print(f"Coordinator 응답: {data.decode()}")
    finally:
        sock.close()

# Monitor 기능 구현
def monitor(sock):
    try:
        print("Monitor가 Coordinator에 연결되었습니다.")
        while True:
            # 주기적으로 polling 메시지 전송
            sock.sendall("polling".encode())
            data = sock.recv(1024)
            if data:
                print(f"Monitor 수신: {data.decode()}")
            else:
                # 연결이 종료됨
                break
            time.sleep(5)  # 5초마다 polling을 반복 수행
    finally:
        sock.close()

# 클라이언트 메인 함수
def client():
    server_address = ('127.0.0.1', 8080)
    
    # TCP/IP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    
    role = input("역할을 선택하세요 (commander/monitor): ").strip().lower()
    
    if role == 'commander':
        commander(sock)
    elif role == 'monitor':
        monitor(sock)
    else:
        print("유효하지 않은 역할입니다. commander 또는 monitor를 선택하세요.")
        sock.close()

if __name__ == "__main__":
    client()
