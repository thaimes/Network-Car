# Main code for controlling RC car
# All controls are mapped for an XBox One controller, adjustments must be made if changed

import cv2.aruco as aruco
import numpy as np
import threading
import requests
import socket
import random
import pygame
import time
import sys
import cv2


UDP_IP = "172.20.10.7" # IPv4 for Rpi 5
UDP_PORT1 = 5005 # Port control
UDP_PORT2 = 5006 # Port miscellaneous
UDP_PORT3 = 5008 # Port power

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT1)
print("UDP target port: %s" % UDP_PORT2)
print("UDP target port: %s" % UDP_PORT3)

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick found. Please connect a joystick.")
    pygame.quit()
    sys.exit()

j = pygame.joystick.Joystick(0)
j.init()
print("Joystick name:", j.get_name())

last_action = None  # Track last printed action

def power():
    MESSAGE = None
    if event.type == pygame.JOYBUTTONDOWN:
        if j.get_button(7):
            print("Power ON")
            MESSAGE = b"ON"

    if MESSAGE is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT3))

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
    TURBO = None
    if event.type == pygame.JOYBUTTONDOWN:
        if j.get_button(0):
            print("A")
            TURBO = b"A"
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
        TURBO = b"STOP"

    if MESSAGE is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT2))

    if TURBO is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(TURBO, (UDP_IP, UDP_PORT1))

def select_game_mode():
    screen = pygame.display.set_mode((850, 550))
    font = pygame.font.SysFont("Consolas", 40)
    modes = ["Easy", "Medium", "Hard", "Free Drive"]
    selected = 0

    while True:
        screen.fill((0, 0, 0))
        title = font.render("Select Game Mode", True, (255, 255, 255))
        screen.blit(title, (250, 50))

        for i, mode in enumerate(modes):
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            text = font.render(mode, True, color)
            screen.blit(text, (300, 150 + i * 60))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:
                    selected = (selected - 1) % len(modes)
                elif event.value[1] == -1:
                    selected = (selected + 1) % len(modes)
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    print(modes[selected])
                    return modes[selected]

def camrunner(screen, mode):
    if mode == "Easy":
        START_TIME = 5 * 60
        COIN_MODE = "gain"
    elif mode == "Medium":
        START_TIME = 3 * 60
        COIN_MODE = "mixed75"
    elif mode == "Hard":
        START_TIME = 2 * 60
        COIN_MODE = "mixed25"
    else:
        START_TIME = float("inf")
        COIN_MODE = "none"

    time_remaining = START_TIME
    last_coin_time = 0
    current_lap = 0
    final_reached = False
    start_time = time.time()

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    STREAM_URL = 'http://172.20.10.7:5000/video_feed'
    stream = requests.get(STREAM_URL, stream=True)
    bytes_buffer = b''
    running = True
    print(f"Game started! Mode: {mode}")

    try:
        for chunk in stream.iter_content(chunk_size=1024):
            if not running or final_reached:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            bytes_buffer += chunk
            a = bytes_buffer.find(b'\xff\xd8')
            b = bytes_buffer.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes_buffer[a:b+2]
                bytes_buffer = bytes_buffer[b+2:]
                img_np = np.frombuffer(jpg, dtype=np.uint8)
                frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                elapsed = time.time() - start_time
                time_remaining = START_TIME - int(elapsed)

                if time_remaining <= 0 and mode != "Free Drive":
                    print("Time's up!")
                    running = False

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = detector.detectMarkers(gray)

                if ids is not None:
                    for marker_id in ids.flatten():
                        if marker_id == 0 and current_lap < 1:
                            current_lap = 1
                            print("Lap 1 reached!")
                        elif marker_id == 1 and current_lap < 2:
                            current_lap = 2
                            print("Lap 2 reached!")
                        elif marker_id == 2 and current_lap == 2:
                            print("Final reached! Game complete!")
                            final_reached = True
                            break
                        elif marker_id == 3 and mode != "Free Drive":
                            now = time.time()
                            if now - last_coin_time > 3:
                                bonus = 15
                                result = "gain"
                                if COIN_MODE == "mixed75":
                                    result = "gain" if random.random() < 0.75 else "lose"
                                elif COIN_MODE == "mixed25":
                                    result = "gain" if random.random() < 0.25 else "lose"

                                if result == "gain":
                                    time_remaining += bonus
                                    start_time += bonus
                                    print("Coin collected! +15s")
                                else:
                                    time_remaining -= bonus
                                    start_time -= bonus
                                    print("Bad coin! -15s")
                                last_coin_time = now

                aruco.drawDetectedMarkers(frame, corners, ids)

                mins = time_remaining // 60 if time_remaining != float("inf") else 99
                secs = time_remaining % 60 if time_remaining != float("inf") else 99
                status = f"⏱ {int(mins):02d}:{int(secs):02d} | Lap: {current_lap}"
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0,1))
                screen.blit(frame_surface, (0, 0))
                pygame.display.update()
    finally:
        # Don't quit the game if the user loses... maybe freeze the feed?
        print("GAME OVER")

def overcurrent():
    UDP_PORT_OC = 5007
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT_OC))
    print(f"Overcurrent detection listening on UDP port {UDP_PORT_OC}")
    while True:
        data, addr = sock.recvfrom(1024)
        if data.strip() == b"OC":
            print("OVERCURRENT")
    
if __name__ == "__main__":
    print("Starting main loop...")
    # Set up a larger display for video + control
    screen = pygame.display.set_mode((850, 550))
    pygame.display.set_caption("RC Car Game")

    game_mode = select_game_mode()

    # Start camera thread
    cam_thread = threading.Thread(target=camrunner, args=(screen, game_mode), daemon=True)
    cam_thread.start()

    # Start overcurrent detection thread
    oc_thread = threading.Thread(target=overcurrent, daemon=True)
    oc_thread.start()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                handle_buzzer(event)
                power()
            handle_control()
            time.sleep(0.01)  # Small delay to avoid high CPU usage
    except KeyboardInterrupt:
        print("Shutdown requested, stopping...")
    print("All tasks completed.")
