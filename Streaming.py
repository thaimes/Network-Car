import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

picam2 = Picamera2()
main = {'size' : (1920, 1080), 'format': 'YUV420'}
controls = {'FrameRate' : 30}
config = picam2.create_video_configuration(main, controls=controls)
picam2.configure(config)

encoder = H264Encoder(bitrate = 1000000)
output = PyavOutput("rtsp://172.20.10.5:8554/cam", format="rtsp")

print("Camera starting")
picam2.start_recording(encoder, output)

try:
    while True:
        #print("Streaming...")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Camera stopping")
