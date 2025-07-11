# Main code for controlling RC car

import socket
import pygame
import time
import sys

UDP_IP = "172.20.10.7" # IPv4 for Rpi 5
UDP_PORT1 = 5005
UDP_PORT2 = 5006

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT1)
print("UDP target port: %s" % UDP_PORT2)

pygame.init()
pygame.joystick.init()

display = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Controller Input Test")

if pygame.joystick.get_count() == 0:
    print("No joystick found. Please connect a joystick.")
    pygame.quit()
    sys.exit()

j = pygame.joystick.Joystick(0)
j.init()
print("Joystick name:", j.get_name())

last_action = None  # Track last printed action

def handle_control():
    global last_action
    lt_value = j.get_axis(4)
    rt_value = j.get_axis(5)
    ls_value = j.get_axis(0)

    action = ""
    if rt_value > 0.5 and ls_value < -0.5:
        action = "FLEFT"
    elif rt_value > 0.5 and ls_value > 0.5:
        action = "FRIGHT"
    elif lt_value > 0.5 and ls_value < -0.5:
        action = "BLEFT"
    elif lt_value > 0.5 and ls_value > 0.5:
        action = "BRIGHT"
    elif rt_value > 0.5:
        action = "FORWARD"
    elif lt_value > 0.5:
        action = "BACK"
    elif ls_value < -0.5:
        action = "LEFT"
    elif ls_value > 0.5:
        action = "RIGHT"
    else:
        action = "HALT"

    if last_action != action:
        print(action)
        last_action = action
        if action:
            MESSAGE = action.encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT1))

def handle_buzzer(event):
    MESSAGE = None
    if event.type == pygame.JOYBUTTONDOWN:
        if j.get_button(0):
            print("A")
            MESSAGE = b"A"
        if j.get_button(1):
            print("B")
            MESSAGE = b"B"
        if j.get_button(2):
            print("X")
            MESSAGE = b"X"
        if j.get_button(3):
            print("Y")
            MESSAGE = b"Tetris"
        if j.get_button(4):
            print("Bumper")
            MESSAGE = b"Bumper"
        if j.get_button(5):
            print("Bumper")
            MESSAGE = b"Bumper"
        if (j.get_button(4) or j.get_button(5)) and j.get_button(1):
            print("Blink")
            MESSAGE = b"BLight"
        if j.get_button(8):
            print("Tetris")
            MESSAGE = b"Tetris"
    if event.type == pygame.JOYBUTTONUP:
        print("STOP")
        MESSAGE = b"STOP"

    if MESSAGE is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT2))

if __name__ == "__main__":
    print("Starting main loop...")
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                handle_buzzer(event)
            handle_control()
            time.sleep(0.01)  # Small delay to avoid high CPU usage
    except KeyboardInterrupt:
        print("Shutdown requested, stopping...")
    print("All tasks completed.")
