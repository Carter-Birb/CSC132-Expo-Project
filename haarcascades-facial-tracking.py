import cv2

# === CONFIG ===
FLIP_CAMERA = True  # Set to True if using front camera, False for back camera
HORIZONTAL_FOV_DEGREES = 70
VERTICAL_FOV_DEGREES = 60

# Load Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Connect to your camera (use DroidCam index or test with 0)
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip horizontally if using front camera (mirrored feed)
    # Check for keyboard input to toggle flipping
    key = cv2.waitKey(1) & 0xFF
    if key == ord('f'):
        FLIP_CAMERA = not FLIP_CAMERA

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        KeyboardInterrupt 

    if FLIP_CAMERA:
        frame = cv2.flip(frame, 1)

    frame_height, frame_width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) > 0:
        # Track the largest face
        faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
        x, y, w, h = faces[0]

        center_x = x + w // 2
        center_y = y + h // 2

        # Normalize offsets
        x_offset = (center_x - frame_width / 2) / (frame_width / 2)
        y_offset = (center_y - frame_height / 2) / (frame_height / 2)

        # Convert to angles
        angle_x = x_offset * (HORIZONTAL_FOV_DEGREES / 2)
        angle_y = y_offset * (VERTICAL_FOV_DEGREES / 2)

        # Estimate distance
        approx_distance = 5000 / w

        # Draw face box and center
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        # Display values
        cv2.putText(frame, f"Angle X: {angle_x:.2f} deg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Angle Y: {angle_y:.2f} deg", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Distance: {approx_distance:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Output tracking data
        print({
            "center_x": center_x,
            "center_y": center_y,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "angle_x": angle_x,
            "angle_y": angle_y,
            "size": w * h,
            "approx_distance": approx_distance
        })

    cv2.imshow("2D Face Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
