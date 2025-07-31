import pygame
import requests
import cv2
import numpy as np

def camrunner():
    # Your Pi's stream URL
    STREAM_URL = 'http://10.161.126.47:5000/video_feed'

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("PiCamera Stream")

    stream = requests.get(STREAM_URL, stream=True)

    bytes_buffer = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes_buffer += chunk
        a = bytes_buffer.find(b'\xff\xd8')  # JPEG start
        b = bytes_buffer.find(b'\xff\xd9')  # JPEG end
        if a != -1 and b != -1:
            jpg = bytes_buffer[a:b+2]
            bytes_buffer = bytes_buffer[b+2:]
       
            img_np = np.frombuffer(jpg, dtype=np.uint8)
            frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            screen.blit(frame_surface, (0, 0))
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

    pygame.quit()

camrunner()
