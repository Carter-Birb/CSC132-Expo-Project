import cv2

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)  # Use 1 if 0 doesn't work

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for better detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    closest_face = None
    max_area = 0

    for (x, y, w, h) in faces:
        area = w * h  # The larger the bounding box, the closer the face
        if area > max_area:
            max_area = area
            closest_face = (x, y, w, h)

    # Draw all detected faces in blue
    for (x, y, w, h) in faces:
        color = (255, 0, 0) if (x, y, w, h) != closest_face else (0, 255, 0)  # Green for closest face
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # Display the video feed
    cv2.imshow("Face Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
