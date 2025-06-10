# UDP Client code to talk to the UDP server on the Rpi 5

import socket
import pygame
import sys

UDP_IP = "172.20.10.4" # IPv4 for Rpi 5
UDP_PORT = 5005

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
#print("message: %s" % MESSAGE)

# Initialize Pygame
pygame.init()

display = pygame.display.set_mode((300, 300))

while True:
    MESSAGE = None # Blank message to start with
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                MESSAGE = b"LEFT"
            if event.key == pygame.K_RIGHT:
                MESSAGE = b"RIGHT"
            if event.key == pygame.K_DOWN:
                MESSAGE = b"BACK"
            if event.key == pygame.K_UP:
                MESSAGE = b"FORWARD"
            
    if MESSAGE != None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))



