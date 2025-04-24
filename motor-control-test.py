import RPi.GPIO as GPIO # This will be underlined if you are not using the RPi.
import time
import keyboard

# Pin definitions
ENA = 20
M0 = 22
M1 = 23
M2 = 24
STEP = 26
DIR = 27

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([ENA, M0, M1, M2, STEP, DIR], GPIO.OUT)

# Set microstepping
MODE = (M0, M1, M2)
RESOLUTION = {'full': (GPIO.LOW, GPIO.LOW, GPIO.LOW, 200),
              'half': (GPIO.HIGH, GPIO.LOW, GPIO.LOW, 400),
              'fourth': (GPIO.LOW, GPIO.HIGH, GPIO.LOW, 800),
              'eighth': (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, 1600),
              'sixteenth': (GPIO.LOW, GPIO.LOW, GPIO.HIGH, 3200),
              'thirty-second': (GPIO.HIGH, GPIO.LOW, GPIO.HIGH, 6400)}

# Set motor to OFF by default
motor_on = False
GPIO.output(ENA, GPIO.HIGH)

# Set motor direction to CCW by default
motor_direction = "CCW"
GPIO.output(DIR, GPIO.HIGH)

# Set to full stepping by default
current_mode = "full"
full_rotation_time = 4 # Seconds
GPIO.output(MODE, RESOLUTION[current_mode][:3])

# Initialize timing variables for pulsing
last_pulse_time = time.time()

def calculate_delay(SPR):
    return (full_rotation_time / SPR)

# Control loop for key presses
try:
    while True:
        # Get the time
        current_time = time.time()
        
        # Adjust delay based on microstep setting
        SPR = RESOLUTION[current_mode][3]
        step_delay = calculate_delay(SPR)
        
        if keyboard.is_pressed('a'): # Press 'a' to move to the previous microstep mode
            modes = list(RESOLUTION.keys())
            current_index = modes.index(current_mode)
            # Move to the previous mode (loop back if necessary)
            current_mode = modes[(current_index - 1) % len(modes)]
            GPIO.output(MODE, RESOLUTION[current_mode][:3])
            print(f"changing microstep setting to {current_mode}") 
            time.sleep(0.5)

        elif keyboard.is_pressed('d'): # Press 'd' to move to the next microstep mode
            modes = list(RESOLUTION.keys())
            current_index = modes.index(current_mode)
            # Move to the next mode (loop back if necessary)
            current_mode = modes[(current_index + 1) % len(modes)]
            GPIO.output(MODE, RESOLUTION[current_mode][:3])
            print(f"changing microstep setting to {current_mode}")
            time.sleep(0.5)

        elif keyboard.is_pressed('s'): # Press 's' to change the direction
            if motor_direction == "CCW":
                motor_direction = "CW"
                GPIO.output(DIR, GPIO.LOW)
                print("motor spinning CW")
                time.sleep(0.5)
                    
            elif motor_direction == "CW":
                motor_direction = "CCW"
                GPIO.output(DIR, GPIO.HIGH)
                print("motor spinning CCW")
                time.sleep(0.5)

        elif keyboard.is_pressed('space'): # Press 'space' to enable/disable the motor
            if motor_on:
                motor_on = False
                GPIO.output(ENA, GPIO.HIGH)
                print("motor off")
                time.sleep(0.5)
                    
            elif not motor_on:
                motor_on = True
                GPIO.output(ENA, GPIO.LOW)
                print("motor on")
                time.sleep(0.5)
                    
        # Spin the motor at a constant rate no matter the microstep setting
        if motor_on:
            # Check if enough time has passed to send the next pulse
            if current_time - last_pulse_time >= step_delay:
                GPIO.output(STEP, GPIO.HIGH)
                time.sleep(0.0005)
                GPIO.output(STEP, GPIO.LOW)
                last_pulse_time = current_time # Update the time of the last pulse

except KeyboardInterrupt:
    GPIO.cleanup()
