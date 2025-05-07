import cv2

class FaceTracker:
    def __init__(self, camera_index=0, flip_camera=True, h_fov=70, v_fov=60, max_distance=100):
        """Initializes the FaceTracker with camera index, field of view, and max distance."""
        self.flip_camera = flip_camera
        self.h_fov = h_fov
        self.v_fov = v_fov
        self.max_distance = max_distance
        self.cap = cv2.VideoCapture(camera_index)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def get_frame(self):
        """Captures and processes a frame, detecting faces and calculating angles."""
        success, frame = self.cap.read()
        if not success:
            return None

        # Flip the frame if required
        if self.flip_camera:
            frame = cv2.flip(frame, 1)

        # Convert frame to grayscale for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # Sort faces based on area (largest face)
            faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
            x, y, w, h = faces[0]

            # Calculate center of the face
            center_x = x + w // 2
            center_y = y + h // 2

            # Calculate offset from the center of the frame
            x_offset = (center_x - frame.shape[1] / 2) / (frame.shape[1] / 2)
            y_offset = (center_y - frame.shape[0] / 2) / (frame.shape[0] / 2)

            # Calculate angles
            self.angle_x = x_offset * (self.h_fov / 2)
            self.angle_y = y_offset * (self.v_fov / 2)

            # Estimate distance
            approx_distance = 5000 / w
            
            if approx_distance > self.max_distance:
                return frame

            # Draw face bounding box and center point
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # Display information on the frame
            cv2.putText(frame, f"Angle X: {self.angle_x:.2f} deg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f"Angle Y: {self.angle_y:.2f} deg", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f"Distance: {approx_distance:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        return frame

    def update_settings(self, flip_camera=None, h_fov=None, v_fov=None, max_distance=None):
        """Update the tracker settings dynamically."""
        if flip_camera is not None:
            self.flip_camera = flip_camera
        if h_fov is not None:
            self.h_fov = h_fov
        if v_fov is not None:
            self.v_fov = v_fov
        if max_distance is not None:
            self.max_distance = max_distance

    def release(self):
        """Release the camera resource."""
        self.cap.release()