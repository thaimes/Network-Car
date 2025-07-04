# UDP Server code to listen for UDP client on PC

import socket
from time import sleep, time
from gpiozero import Motor, AngularServo


motor = Motor(forward = 17, backward = 24, enable = 18, pwm = True)
st_servo = 25

steering = AngularServo(
    st_servo,
    min_angle = 0,
    max_angle = 180,
    min_pulse_width = 0.5/1000,
    max_pulse_width = 2.5/1000
)
steering.angle = 90
steering.detach()
angles = [30,90,150]

#for angle in angles:
def turn(angle):
    steering.detach()
    steering.angle = angle
    #print(f"Steering to {angle}°")
   # sleep(0.2)           # wait so servo has time to move
    steering.detach()
   # sleep(0.1)
    
UDP_IP = "0.0.0.0" # IPv4 IP for PC
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

last_command = None



def execute(command):
    global last_command
    if command == last_command:
        return
    last_message = command

    
    if command == b'LEFT':
        motor.stop()
        steering.angle = angles[0]
        print("TURNING LEFT")
        
        
    elif command == b'RIGHT':
        motor.stop()
        steering.angle = angles[2]
        print("TURNING RIGHT")
        
    
    elif command == b'BACK':
        motor.backward()
        steering.angle = angles[1] 
        print("BACKING UP")
        
    elif command == b'FORWARD':
        motor.forward()
        steering.angle = angles[1] 
        print("GOING FORWARD")
    
    elif command == b'FORWARD AND LEFT':
        motor.forward()
        steering.angle = angles[0]
        print("GOING FORWARD AND TURNING LEFT")
    
    elif command == b'FORWARD AND RIGHT':
        motor.forward()
        steering.angle = angles[2]
        print("GOING FORWARD AND TURNING RIGHT")
    
    elif command == b'BACKING AND RIGHT':
        motor.backward()
        steering.angle = angles[0]
        print("BACKING UP AND TURNING RIGHT")
    
    elif command == b'BACKING AND LEFT':
        motor.backward()
        steering.angle = angles[2]
        print("BACKING UP AND TURNING LEFT")
        
    else:
        motor.stop()
        steering.angle = angles[1]
        

while True:
    data, addr = sock.recvfrom(1024)
    execute(data)
