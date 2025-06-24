# Main python file for Network Controlled RC Car
# Protocols used are:
# - UDP (motor control)
# - RTSP (video streaming)
# Program achieves paralleism via threading to allow for camera feed and car control simultaneously

import threading
import socket
import time
from time import sleep
from gpiozero import Motor, AngularServo
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

# UDP Server Setup
    
UDP_IP = "0.0.0.0" # IPv4 address for PC
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
################################################################3
# Camera Streaming Setup
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={'size': (1280, 720), 'format': 'YUV420'},
    controls={'FrameRate': 30}
)
picam2.configure(config)
encoder = H264Encoder(bitrate=1000000)
output = PyavOutput("rtsp://172.20.10.3:8554/cam", format="rtsp")

# Shared stop-event for clean exit
stop_event = threading.Event()

def control():
    motor = Motor(forward = 4, backward = 24)
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

    def turn(angle):
        steering.detach()
        steering.angle = angle
        sleep(.2)           # wait so servo has time to move
        steering.detach()
        sleep(0.5)
        
    while not stop_event.is_set():
        data, addr = sock.recvfrom(1024)
        
        if data == b'LEFT':
            motor.stop()
            steering.angle = angles[2]
            print("TURNING LEFT")
            
        elif data == b'RIGHT':
            motor.stop()
            steering.angle = angles[0]
            print("TURNING RIGHT")
            
        elif data == b'BACK':
            motor.backward()
            steering.angle = angles[1] 
            print("BACKING UP")
            
        elif data == b'FORWARD':
            motor.forward()
            steering.angle = angles[1] 
            print("GOING FORWARD")
        
        elif data == b'FORWARD AND LEFT':
            motor.forward()
            steering.angle = angles[2]
            print("GOING FORWARD AND TURNING LEFT")
        
        elif data == b'FORWARD AND RIGHT':
            motor.forward()
            steering.angle = angles[0]
            print("GOING FORWARD AND TURNING RIGHT")
        
        elif data == b'BACKING AND RIGHT':
            motor.backward()
            steering.angle = angles[2]
            print("BACKING UP AND TURNING RIGHT")
        
        elif data == b'BACKING AND LEFT':
            motor.backward()
            steering.angle = angles[0]
            print("BACKING UP AND TURNING LEFT")
            
        else:
            motor.stop()
            steering.angle = angles[1] 

def camera():
    picam2.start_recording(encoder, output)
    while not stop_event.is_set():
        time.sleep(0.5)
    picam2.stop_recording()

####################################################
# Main
if __name__ == "__main__":
    print("Starting threads...")
    t1 = threading.Thread(target=control)
    t2 = threading.Thread(target=camera)

    t1.start()
    t2.start()

    try:
        while t1.is_alive() and t2.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutdown requested, stopping threads...")
        stop_event.set()

    t1.join()
    t2.join()
    print("All tasks completed.")

