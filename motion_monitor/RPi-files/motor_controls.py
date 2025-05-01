import requests
import time
import RPi.GPIO as GPIO

# The URL of the Flask server
FLASK_SERVER_URL = "http://138.47.250.27:5000/get_motor_commands"

# Motor pins configuration
DIR_PIN = 27
STEP_PIN = 26
M0_PIN = 22
M1_PIN = 23
M2_PIN = 24
ENA_PIN = 20

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([DIR_PIN, STEP_PIN, M0_PIN, M1_PIN, M2_PIN, ENA_PIN], GPIO.OUT)

# Stepper motor settings
MICROSTEPPING = 4  # Options: 1, 2, 4, 8, 16, 32
MAX_STEPS = 126
MIN_POSITION = 0
MAX_POSITION = MAX_STEPS / (1.8 / MICROSTEPPING)  # Based on microstepping
SPEED = 1  # Seconds per full rotation

# Motor control resolution based on microstepping
MICROSTEPPING_MODES = {
    1: (GPIO.LOW, GPIO.LOW, GPIO.LOW),
    2: (GPIO.HIGH, GPIO.LOW, GPIO.LOW),
    4: (GPIO.LOW, GPIO.HIGH, GPIO.LOW),
    8: (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
    16: (GPIO.LOW, GPIO.LOW, GPIO.HIGH),
    32: (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
}

# Set microstepping mode
GPIO.output((M0_PIN, M1_PIN, M2_PIN), MICROSTEPPING_MODES[MICROSTEPPING])

# Timer for step pulses
last_step_time = time.time()
step_interval = SPEED / (MICROSTEPPING * 200)

# Motor position tracking (initial position set to center)
current_position = int(MAX_POSITION / 2)
motor_direction = ""

def fetch_motor_commands():
    """Fetch motor commands from the Flask server."""
    try:
        response = requests.post(FLASK_SERVER_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching motor commands: {e}")
    return None

def set_motor_direction(direction):
    """Set the motor's rotation direction (clockwise or counterclockwise)."""
    if direction == "CCW":
        GPIO.output(DIR_PIN, GPIO.HIGH)  # Counterclockwise
    elif direction == "CW":
        GPIO.output(DIR_PIN, GPIO.LOW)   # Clockwise

def send_motor_pulse():
    """Send a pulse to the stepper motor to take a step."""
    global last_step_time, current_position
    
    # Get the current time
    current_time = time.time()

    # If enough time has passed since the last pulse, send a pulse
    if current_time - last_step_time >= step_interval:
        GPIO.output(STEP_PIN, GPIO.HIGH)  # Start pulse
        time.sleep(0.001)
        GPIO.output(STEP_PIN, GPIO.LOW)   # End pulse

        # Update the motor position based on direction
        if motor_direction == "CCW":
            current_position += 1  # Moving counterclockwise
        elif motor_direction == "CW":
            current_position -= 1  # Moving clockwise

        last_step_time = current_time  # Update last pulse time
        print(f"Motor position: {current_position} steps")

def recalibrate_motor():
    """Recalibrate the motor by moving it to the center position."""
    global current_position, motor_direction

    # Calculate the center position
    center_position = int(MAX_POSITION / 2)

    # Determine direction to center the motor
    if current_position < center_position:
        set_motor_direction("CCW")
        motor_direction = "CCW"
    elif current_position > center_position:
        set_motor_direction("CW")
        motor_direction = "CW"

    # Enable the motor and move it towards the center
    GPIO.output(ENA_PIN, GPIO.LOW)

    steps_needed = abs(current_position - center_position)
    for _ in range(steps_needed):
        send_motor_pulse()

def main():
    global motor_direction

    while True:
        # Get motor commands from the Flask server
        motor_commands = fetch_motor_commands()

        if motor_commands:
            motor_on = motor_commands['motor_on']
            motor_direction = motor_commands['direction']

            if motor_on:
                GPIO.output(ENA_PIN, GPIO.LOW)  # Enable the motor
                set_motor_direction(motor_direction)

                # Boundaries check: Stop if motor reaches limits
                if (motor_direction == "CW" and current_position <= MIN_POSITION) or \
                   (motor_direction == "CCW" and current_position >= MAX_POSITION):
                    GPIO.output(ENA_PIN, GPIO.HIGH)  # Disable motor
                    print("Motor has hit boundary")
                else:
                    # Send a step pulse to move the motor
                    send_motor_pulse()

            else:
                print("Motor is off")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        recalibrate_motor()  # Recalibrate the motor to the center position
        GPIO.cleanup()  # Cleanup GPIO pins before exiting