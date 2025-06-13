# Controller test code to replace keyboard code

import socket
import pygame
import sys
import time

UDP_IP = "172.20.10.4" # IPv4 for Rpi 5
UDP_PORT = 5005

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

pygame.init()
pygame.joystick.init()

display = pygame.display.set_mode((300, 300))

if pygame.joystick.get_count() == 0:
    print("No joystick found!")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Joystick name:", joystick.get_name())

# Joystick axis mapping
L_X = 0
L_TRIG = 4
R_TRIG = 5

# Track latest axis values
axis_values = {
    L_X: 0.0,
    L_TRIG: 0.0,
    R_TRIG: 0.0
}

while True:
    MESSAGE = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.JOYAXISMOTION:
            axis_values[event.axis] = event.value  # Value tracking

    MESSAGE = b""

    lx = axis_values[L_X]
    lt = axis_values[L_TRIG]
    rt = axis_values[R_TRIG]

    if rt > 0.5 and lx < -0.5:
        MESSAGE = b"FORWARD AND LEFT"
    elif rt > 0.5 and lx > 0.5:
        MESSAGE = b"FORWARD AND RIGHT"
    elif lt > 0.5 and lx < -0.5:
        MESSAGE = b"BACKING AND RIGHT"
    elif lt > 0.5 and lx > 0.5:
        MESSAGE = b"BACKING AND LEFT"
    elif rt > 0.5:
        MESSAGE = b"FORWARD"
    elif lt > 0.5:
        MESSAGE = b"BACK"
    elif lx < -0.5:
        MESSAGE = b"LEFT"
    elif lx > 0.5:
        MESSAGE = b"RIGHT"

   # time.sleep(0.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# Small issues
# - Currently has delay between messages
