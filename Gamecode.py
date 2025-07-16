import cv2
import cv2.aruco as aruco
import time

# Game configuration
START_TIME = 3 * 60  # 3 minutes in seconds
time_remaining = START_TIME
last_coin_time = 0

# Game state
current_lap = 0
final_reached = False

# ArUco setup
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Start cam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open camera.")
    exit()

# Start game clock
start_time = time.time()
print("Game started! Time: 3:00")

while cap.isOpened() and not final_reached:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Update timer
    elapsed = time.time() - start_time
    time_remaining = START_TIME - int(elapsed)

    if time_remaining <= 0:
        print("Time's up!")
        break

    # Detect markers
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
                if now - last_coin_time > 3:  # 3-second cooldown
                    time_remaining += 15
                    start_time += 15  # shift clock to reflect time add
                    last_coin_time = now
                    print("Coin collected! +15s")

    # Draw markers
    aruco.drawDetectedMarkers(frame, corners, ids)

    # Display timer and lap
    mins = time_remaining // 60
    secs = time_remaining % 60
    timer_str = f"⏱ {int(mins):02d}:{int(secs):02d} | Lap: {current_lap}"
    cv2.putText(frame, timer_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("RC Car Game", frame)

    # Exit on ESC key
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        print("Game cancelled")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
