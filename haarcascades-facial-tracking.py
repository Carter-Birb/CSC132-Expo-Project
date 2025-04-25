import cv2

# === CONFIGURATION ===
FLIP_CAMERA = True  # True = front camera (mirrored), False = back camera (non-mirrored)
HORIZONTAL_FOV_DEGREES = 70  # Horizontal field of view of the camera
VERTICAL_FOV_DEGREES = 60    # Vertical field of view of the camera

# === INITIALIZE ===
# Load Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Open camera (0 = default camera or replace with DroidCam index)
cap = cv2.VideoCapture(0)

# === MAIN LOOP ===
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Handle key input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('f'):
        FLIP_CAMERA = not FLIP_CAMERA  # Toggle camera flip
    elif key == ord('q'):
        break  # Quit the loop

    # Mirror the frame if using the front camera
    if FLIP_CAMERA:
        frame = cv2.flip(frame, 1)

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) > 0:
        # Sort faces by size (area), descending — focus on the largest face
        faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
        x, y, w, h = faces[0]  # Get the largest face

        # Calculate the center of the face
        center_x = x + w // 2
        center_y = y + h // 2

        # Normalize offsets (-1 to 1)
        x_offset = (center_x - frame.shape[1] / 2) / (frame.shape[1] / 2)
        y_offset = (center_y - frame.shape[0] / 2) / (frame.shape[0] / 2)

        # Convert offsets to angles using FOV
        angle_x = x_offset * (HORIZONTAL_FOV_DEGREES / 2)
        angle_y = y_offset * (VERTICAL_FOV_DEGREES / 2)

        # Estimate distance based on face width (simple approximation)
        approx_distance = 5000 / w  # Arbitrary scale factor for distance

        # === DISPLAY INFO ON FRAME ===
        # Draw bounding box and center dot on the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        # Show calculated angles and estimated distance
        cv2.putText(frame, f"Angle X: {angle_x:.2f} deg", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Angle Y: {angle_y:.2f} deg", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(frame, f"Distance: {approx_distance:.2f}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # === PRINT TRACKING DATA ===
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

    # Show the processed frame
    cv2.imshow("2D Face Tracker", frame)

# === CLEANUP ===
cap.release()
cv2.destroyAllWindows()