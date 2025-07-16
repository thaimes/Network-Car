from flask import Flask, Response
import picamera
import time

app = Flask(__name__)

def generate_frames():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        time.sleep(2)
        stream = camera.capture_continuous(format='jpeg', use_video_port=True)
        for frame in stream:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.getvalue() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "PiCamera Stream Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
