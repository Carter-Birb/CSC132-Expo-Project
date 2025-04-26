from flask import Flask, render_template, Response, jsonify, request
from face_tracker import FaceTracker
import webbrowser
import threading
import cv2  # Import cv2 to handle image encoding

app = Flask(__name__)
tracker = FaceTracker(camera_index=1)  # Initialize the FaceTracker

# Motor settings
MICROSTEPPING = 8  # Accepts 1, 2, 4, 8, 16, 32 microstepping
DEGREERANGE = 126  # FOV in degrees the monitor can move
MINPOS = 0  # Steps
MAXPOS = DEGREERANGE / (1.8 / MICROSTEPPING)

# Initialize video feed generator
def generate_frames():
    """Generate video frames for streaming."""
    while True:
        frame = tracker.get_frame()  # Get the frame from the FaceTracker
        if frame is None:
            break

        _, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Serve the video feed to the frontend."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_config', methods=['POST'])
def set_config():
    """Handle configuration updates for the tracker."""
    data = request.form
    flip = data.get('flip') == 'true'
    max_distance = float(data.get('max_distance', 100))

    tracker.update_settings(flip_camera=flip, max_distance=max_distance)  # Update the tracker settings
    return '', 204

@app.route('/get_motor_commands', methods=['POST'])
def get_motor_commands():
    """Get motor commands based on face position."""
    motor_commands = {
        "direction": "",
        "motor_on": False,
    }
    angle_x = tracker.angle_x  # Get the current angle of the face

    # Determine motor commands based on angle_x
    if angle_x > 2:
        motor_commands['motor_on'] = True
        motor_commands['direction'] = "CW"
    elif angle_x < -2:
        motor_commands['motor_on'] = True
        motor_commands['direction'] = "CCW"
    else:
        motor_commands['motor_on'] = False  # No movement needed if angle is within range
    
    return jsonify(motor_commands)

def open_browser():
    """Open the browser automatically when the server starts."""
    webbrowser.open("http://localhost:5000")

if __name__ == '__main__':
    # Open the browser in a separate thread
    threading.Timer(1.0, open_browser).start()
    
    # Start the Flask app (use `debug=True` for development)
    app.run(host='0.0.0.0', port=5000, debug=False)