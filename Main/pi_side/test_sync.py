import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import os
import shutil
import sys
# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BOARD)

# Define the GPIO pins
clock_in = 16
me_ready = 19
other_ready = 21

# Set up the GPIO pin as an input with a pull-up resistor
GPIO.setup(clock_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(me_ready, GPIO.OUT)
GPIO.setup(other_ready, GPIO.IN)


def scp(local_ip, local_user, local_dir, file):
    command = ["scp", "-P2222", file, local_user + "@" +
               local_ip + ":/home/" + local_user + local_dir]
    subprocess.run(command)


# initialize file directory
sound_dir = "bytes/"

if sys.argv[1] != "sec":
    GPIO.output(me_ready, GPIO.LOW)
    input("Press Enter to start polling.")

try:
    if sys.argv[1] == "main":
        check_test_ready = "/home/" + sys.argv[2] + "/test_ready.txt"
        while True:
            while not os.path.exists(check_test_ready):
                time.sleep(0.0000001)
            GPIO.output(me_ready, GPIO.HIGH)
            if GPIO.input(other_ready) == GPIO.LOW:
                GPIO.wait_for_edge(other_ready, GPIO.FALLING)

            GPIO.output(me_ready, GPIO.LOW)
            GPIO.wait_for_edge(clock_in, GPIO.FALLING)

            current_time = time.time()

            with open(sound_dir + sys.argv[2] + "_time.txt", 'w') as file:
                file.write(str(current_time))

            os.remove(check_test_ready)

            # send the time and file to inform sent
            scp("127.0.0.1", "simon", "/EEE3097_Repo_2/EEE3097S/Main/bytes",
                sound_dir + sys.argv[2] + "_time.txt")
            scp("127.0.0.1", "simon", "/EEE3097_Repo_2/EEE3097S/Main",
                sys.argv[2] + "_finnished.txt")
    elif sys.argv[1] == "sec":
        while True:
            GPIO.output(me_ready, GPIO.HIGH)
            if GPIO.input(other_ready) == GPIO.LOW:
                GPIO.wait_for_edge(other_ready, GPIO.FALLING)
            GPIO.output(me_ready, GPIO.LOW)
            GPIO.wait_for_edge(clock_in, GPIO.FALLING)

            current_time = time.time()

            with open(sound_dir + sys.argv[2] + "_time.txt", 'w') as file:
                file.write(str(current_time))

            # send the time and file to inform sent
            scp("127.0.0.1", "simon", "/EEE3097_Repo_2/EEE3097S/Main/bytes",
                sound_dir + sys.argv[2] + "_time.txt")
            scp("127.0.0.1", "simon", "/EEE3097_Repo_2/EEE3097S/Main",
                sys.argv[2] + "_finnished.txt")
    else:
        print("Invalid device type. <device = 'main'/'sec'>")

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
