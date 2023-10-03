import RPi.GPIO as GPIO
import time
import subprocess
import os
import shutil

directory_path = "/home/simon/bytes"
if os.path.exists(directory_path):
        shutil.rmtree(directory_path)  # Remove the directory and its contents
        print(f"Deleted directory and its contents: {directory_path}")

# Recreate the directory
os.mkdir(directory_path)
print(f"Recreated directory: {directory_path}")

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BOARD)

# Define the GPIO pin to monitor
input_pin = 16  # Change this to the desired GPIO pin number

# Set up the GPIO pin as an input with a pull-up resistor
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialize number of sound bytes recorded
num_bytes = 0

# initialize base command
arecord_command = [
    "arecord",
    "-D", "plughw:0",
    "-c", "1",
    "-r", "48100",
    "-f", "S32_LE",
    "-t", "wav",
    "-s", "5000",
    "-V", "mono",
    "-v"
]

# initialize file directory
dir = "bytes/"

try:
    while True:
        GPIO.wait_for_edge(input_pin, GPIO.FALLING)
        subprocess.run(arecord_command + [dir +"byte_" + str(num_bytes) + ".wav"])  # Corrected this line
        #current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        #print(f"Falling edge detected at {current_time}")
        num_bytes += 1

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()

