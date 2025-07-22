# Main python file for Network Controlled RC Car
# Protocols used are:
# - UDP (motor control)
# - RTSP (video streaming)
# Program achieves paralleism via threading to allow for camera feed and car control simultaneously

import threading
import socket
import time
import cv2
import io
import numpy as np
from time import sleep
from signal import pause
from gpiozero import Motor, AngularServo, LED, Button, TonalBuzzer, DigitalInputDevice, Servo
from gpiozero.tones import Tone
from picamera2 import Picamera2
from flask import Flask, Response

# UDP Server Setup
    
UDP_IP = "0.0.0.0" # IPv4 address for PC
sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_control.bind((UDP_IP, 5005))

sock_honker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_honker.bind((UDP_IP, 5006))


################################################################3
# Camera Streaming Setup
app = Flask(__name__)

# Initialize camera once
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (850, 550)}))

picam2.start()


#######################################################################
# Buzzer setup
led=LED(6)
pow_button=Button(23)
led.off()

buzzer=TonalBuzzer(27)
led_index=0 
       
# Shared stop-event for clean exit
stop_event = threading.Event()
OC_event = threading.Event()

def honker():
    
    NOTE_E5= 659.25
    NOTE_B4 = 493.88
    NOTE_C5 = 523.25
    NOTE_D5 = 587.33
    NOTE_A4=440.00
    NOTE_G4=392.00
    NOTE_F5=698.46
    NOTE_A5=880.00
    NOTE_G5=783.99
        
    melody=[
        NOTE_E5, NOTE_B4, NOTE_C5, NOTE_D5,
        NOTE_C5, NOTE_B4, NOTE_A4, NOTE_A4,
        NOTE_C5, NOTE_E5, NOTE_D5, NOTE_C5,
        NOTE_B4, NOTE_C5, NOTE_D5, NOTE_E5,
        NOTE_C5, NOTE_A4, NOTE_A4  ]
        
    durations= [4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8]
    
    #if power_button pressed
    def switch_led():
        global led_index
        if led_index==1: 
            led.off()
            led_index=0
            
        elif led_index==0:
        #Power Startup = Lights and Sound
            led.on()
            buzzer.play(808.61)
            sleep(0.25)
            led.off()
            buzzer.play(622.25)
            sleep(0.3)
            led.on()
            buzzer.play(415.30)
            sleep(0.3)
            led.off()
            buzzer.play(466.16)
            sleep(0.6)
            led.on()
            buzzer.stop()
            led_index=1
            

    def buzzer_off():
        buzzer.stop()
        

    pow_button.when_pressed=switch_led

    while not stop_event.is_set():
        data, addr = sock_honker.recvfrom(1024)
        print(data)
        
        if led_index==1:
            if data == b'B':
                print("HONK")
                buzzer.play(440)

            elif data==b'Tetris':
                for i in range(len(melody)):
                    duration_ms=1000/durations[i]
                
                    buzzer.play(melody[i])
                    sleep(duration_ms/1000)
                    buzzer.stop()

            elif data==b'Bumper':
                led.on()
                sleep(0.25)
                led.off()
                sleep(0.25)
        
            elif data==b'BLight':
                led.on()
                buzzer.play(440)
                sleep(0.25)
                led.off()
                buzzer.stop()

            else:
                led.on()
                buzzer.stop()
        else:
            led.off()
            buzzer.stop()
            
def control():
    global motor
    motor = Motor(forward=24, backward=17, enable=18, pwm=True)
    st_servo = 25
    steering = AngularServo(
        st_servo,
        min_angle=0,
        max_angle=180,
        min_pulse_width=0.6 / 1000,
        max_pulse_width=2.4 / 1000
    )
    
    # Store last angle to avoid re-setting same value
    last_angle = None
    angles = [30, 90, 150]

    def turn(angle):
        nonlocal last_angle
        if angle != last_angle:
            steering.angle = angle
            sleep(0.3)      # Give it time to move
            steering.detach()
            last_angle = angle

    turn(angles[1])  # Start centered

    while not stop_event.is_set():
        data, addr = sock_control.recvfrom(1024)

        if led_index == 1:
            if data == b'LEFT':
                motor.stop()
                turn(angles[0])
                print("TURNING LEFT")

            elif data == b'RIGHT':
                motor.stop()
                turn(angles[2])
                print("TURNING RIGHT")

            elif data == b'BACK':
                motor.backward(speed=0.85)
                turn(angles[1])
                print("BACKING UP")

            elif data == b'FORWARD':
                motor.forward(speed=0.85)
                turn(angles[1])
                print("GOING FORWARD")

            elif data == b'FLEFT':
                motor.forward(speed=0.85)
                turn(angles[0])
                print("GOING FORWARD AND TURNING LEFT")

            elif data == b'FRIGHT':
                motor.forward(speed=0.85)
                turn(angles[2])
                print("GOING FORWARD AND TURNING RIGHT")

            elif data == b'BRIGHT':
                motor.backward(speed=0.85)
                turn(angles[0])
                print("BACKING UP AND TURNING RIGHT")

            elif data == b'BLEFT':
                motor.backward(speed=0.85)
                turn(angles[2])
                print("BACKING UP AND TURNING LEFT")

            elif data == b'A':
                motor.forward()
                turn(angles[1])
                print("TURBO")

            else:
                motor.stop()
                turn(angles[1])

        else:
            motor.stop()
            turn(angles[1])
 

def camdamn():
    def generate_frames():
        while True:
            frame = picam2.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

            if not ret:
                continue
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=5000, threaded=True)

####################################################

def overcurrent():
    overcurrent_pin = DigitalInputDevice(26)
    debounce_time = 0.5  # Seconds the pin must stay safe before clearing

    def monitor():
        while not stop_event.is_set():
            if overcurrent_pin.value == 1:
                time.sleep(0.5)
                if overcurrent_pin.value == 1:
                    OC_event.is_set()
                    print("OC")
                    motor.stop()
                else:
                    OC_event.clear()
            else:
                OC_event.clear()
    threading.Thread(target=monitor, daemon=True).start()
    pause()  # Keep GPIO thread alive


# Main
if __name__ == "__main__":
    print("Starting threads...")
    t1 = threading.Thread(target=control)
    t2 = threading.Thread(target=honker)
    t3 = threading.Thread(target=camdamn)
    t4 = threading.Thread(target=overcurrent)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    try:
        while t1.is_alive() and t2.is_alive() and t3.is_alive and t4.is_alive:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutdown requested, stopping threads...")
        stop_event.set()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    print("All tasks completed.")
    

