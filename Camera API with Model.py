import cv2
import dlib

detector = dlib.get_frontal_face_detector()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    closest_face = None
    max_area = 0

    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        area = w * h
        if area > max_area:
            max_area = area
            closest_face = (x, y, w, h)

    # Draw faces
    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        color = (255, 0, 0) if (x, y, w, h) != closest_face else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv2.imshow("Face Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
