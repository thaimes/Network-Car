# Controller test code to replace keyboard code
import socket
import pygame
import sys

UDP_IP = "172.20.10.7" # IPv4 for Rpi 5
UDP_PORT = 5005

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

pygame.init()
pygame.joystick.init()

display = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Controller Input Test")

if pygame.joystick.get_count() == 0:
    print("No joystick found. Please connect a joystick.")
    pygame.quit()
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Joystick name:", joystick.get_name())

lt_pressed = False  # Track LT state
rt_pressed = False  # Track RT state
lsl_pressed = False  # Track LS state left
lsr_pressed = False  # Track LS state right
last_action = None  # Track last printed action

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    lt_value = joystick.get_axis(4)
    rt_value = joystick.get_axis(5)
    ls_value = joystick.get_axis(0)

    # Determine combined states
    action = None
    MESSAGE = None

    if rt_value > 0.5 and ls_value < -0.5:
        action = "FORWARD AND LEFT"
        MESSAGE = b"FLEFT"
    elif rt_value > 0.5 and ls_value > 0.5:
        action = "FORWARD AND RIGHT"
        MESSAGE = b"FRIGHT"
    elif lt_value > 0.5 and ls_value < -0.5:
        action = "BACKWARD AND LEFT"
        MESSAGE = b"BLEFT"
    elif lt_value > 0.5 and ls_value > 0.5:
        action = "BACKWARD AND RIGHT"
        MESSAGE = b"BRIGHT"
    elif rt_value > 0.5:
        action = "FORWARD"
        MESSAGE = b"FORWARD"        
    elif lt_value > 0.5:
        action = "BACK"
        MESSAGE = b"BACK"
    elif ls_value < -0.5:
        action = "LEFT"
        MESSAGE = b"LEFT"
    elif ls_value > 0.5:
        action = "RIGHT"
        MESSAGE = b"RIGHT"
    else:
        action = "HALT"
        MESSAGE = b""

    if last_action != action:
        print(action)
        last_action = action


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))



# Controller mapping (PS5 controller being used, update to XBOX controller at lab)
# LT = Axis 4
# RT = Axis 5
# LS = Axis 0
