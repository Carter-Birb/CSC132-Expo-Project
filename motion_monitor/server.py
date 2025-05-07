from flask import Flask, render_template, Response, jsonify, request
from face_tracker import FaceTracker
import webbrowser
import threading
import cv2
from time import sleep
import os

app = Flask(__name__)

tracker = FaceTracker(camera_index=0)
quit = False

# Motor settings
MICROSTEPPING = 8
DEGREERANGE = 126
MINPOS = 0
MAXPOS = DEGREERANGE / (1.8 / MICROSTEPPING)

# --- NEW: Motor enable toggle ---
motor_enabled = True

def generate_frames():
    while True:
        frame = tracker.get_frame()
        if frame is None:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', motor_enabled=motor_enabled)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_config', methods=['POST'])
def set_config():
    global quit, motor_enabled
    data = request.form
    if data.get('quit') == 'true':
        quit = True
        print("Quit flag set. Sending final response to RPI...")
        sleep(1)
        shutdown_server()
        return jsonify({"message": "Server is shutting down..."}), 200

    # Handle other configuration updates
    if 'flip' in data:
        flip = data.get('flip') == 'true'
        tracker.update_settings(flip_camera=flip)
    if 'max_distance' in data:
        max_distance = float(data.get('max_distance', 100))
        tracker.update_settings(max_distance=max_distance)
    # --- NEW: Motor enable toggle ---
    if 'motor_enabled' in data:
        motor_enabled = data.get('motor_enabled') == 'true'
    return '', 204

def shutdown_server():
    print("Shutting down the server...")
    os._exit(0)

@app.route('/get_motor_commands', methods=['POST'])
def get_motor_commands():
    global motor_enabled
    motor_commands = {
        "direction": "",
        "motor_on": False,
        "quit": quit,
    }
    angle_x = tracker.angle_x
    # --- NEW: Respect motor_enabled toggle ---
    if not motor_enabled:
        motor_commands['motor_on'] = False
        motor_commands['direction'] = ""
    else:
        if angle_x > 2:
            motor_commands['motor_on'] = True
            motor_commands['direction'] = "CW"
        elif angle_x < -2:
            motor_commands['motor_on'] = True
            motor_commands['direction'] = "CCW"
        else:
            motor_commands['motor_on'] = False
    return jsonify(motor_commands)

def open_browser():
    webbrowser.open("http://localhost:5000")

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
