import cv2.aruco as aruco
import numpy as np
import requests
import pygame
import time
import cv2

# Game Setup
START_TIME = 3 * 60
time_remaining = START_TIME
last_coin_time = 0
current_lap = 0
final_reached = False
start_time = time.time()

# ArUco Setup
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Stream Setup
STREAM_URL = 'http://10.161.126.47:5000/video_feed'
stream = requests.get(STREAM_URL, stream=True)
bytes_buffer = b''

# Pygame Setup 
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("RC Car Game")

# Main Loop 
running = True
print("Game started! Time: 3:00")

while running and not final_reached:
    # Process Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read stream data
    chunk = next(stream.iter_content(chunk_size=1024))
    bytes_buffer += chunk
    a = bytes_buffer.find(b'\xff\xd8')
    b = bytes_buffer.find(b'\xff\xd9')

    if a != -1 and b != -1:
        jpg = bytes_buffer[a:b+2]
        bytes_buffer = bytes_buffer[b+2:]

        img_np = np.frombuffer(jpg, dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        #Game Logic
        elapsed = time.time() - start_time
        time_remaining = START_TIME - int(elapsed)

        if time_remaining <= 0:
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
                elif marker_id == 3:
                    now = time.time()
                    if now - last_coin_time > 3:
                        time_remaining += 15
                        start_time += 15
                        last_coin_time = now
                        print("Coin collected! +15s")

        # Marker frames
        aruco.drawDetectedMarkers(frame, corners, ids)

        # Overlay timer and lap
        mins = time_remaining // 60
        secs = time_remaining % 60
        status = f"⏱ {int(mins):02d}:{int(secs):02d} | Lap: {current_lap}"
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Convert BGR to RGB for Pygame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create surface and display
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame))
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()

pygame.quit()
