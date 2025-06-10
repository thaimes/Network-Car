# UDP Server code to listen for UDP client on PC

import socket

UDP_IP = "0.0.0.0" # IPv4 IP for PC
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    
    if data == b'LEFT':
        print("TURNING LEFT")
    if data == b'RIGHT':
        print("TURNING RIGHT")
    if data == b'BACK':
        print("BACKING UP")
    if data == b'FORWARD':
        print("GOING FORWARD")

