import RPi.GPIO as GPIO
import time
import subprocess
import os
import shutil
import sys

if len(sys.argv) != 4:
    print("Incorrect number of arguments. <device = 'main'/'sec'> <pi_name>")
    GPIO.cleanup()
    sys.exit()

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

# initialize base command
arecord_mono = [
    "arecord",
    "-D", "plughw:0",
    "-c", "1",
    "-r", "48100",
    "-f", "S32_LE",
    "-t", "wav",
    "-s", "10000",
    "-V", "mono",
    "-v"
]

arecord_stereo = ["arecord", "-D", "plughw:0", "-c2", "-r",
                  "48000", "-f", "S32_LE", "-t", "wav", "-V", "stereo", "-v"]

if sys.argv[3] == "mono":
    arecord = arecord_mono
elif sys.argv[3] == "stereo":
    arecord = arecord_stereo
else:
    print("Invalid record type. <stereo = 'mono'/'stereo'>")
    GPIO.cleanup()
    sys.exit()


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
        check_pc_ready = "/home/" + sys.argv[2] + "/pc_ready.txt"
        while True:
            while not os.path.exists(check_pc_ready):
                time.sleep(0.000001)
            GPIO.output(me_ready, GPIO.HIGH)
            if GPIO.input(other_ready) == GPIO.LOW:
                GPIO.wait_for_edge(other_ready, GPIO.FALLING)
            GPIO.output(me_ready, GPIO.LOW)
            GPIO.wait_for_edge(clock_in, GPIO.FALLING)
            subprocess.run(
                arecord + [sound_dir + sys.argv[2] + "_next_byte.wav"])
            os.remove(check_pc_ready)
            scp("127.0.0.1", "simon", "/pi_sync/bytes",
                sound_dir + sys.argv[2] + "_next_byte.wav")
            scp("127.0.0.1", "simon", "/pi_sync",
                sys.argv[2] + "_finnished.txt")
    elif sys.argv[1] == "sec":
        while True:
            GPIO.output(me_ready, GPIO.HIGH)
            if GPIO.input(other_ready) == GPIO.LOW:
                GPIO.wait_for_edge(other_ready, GPIO.FALLING)
            GPIO.output(me_ready, GPIO.LOW)
            GPIO.wait_for_edge(clock_in, GPIO.FALLING)
            subprocess.run(arecord + [sound_dir + "rpi2_next_byte.wav"])
            scp("127.0.0.1", "simon", "/pi_sync/bytes",
                sound_dir + sys.argv[2] + "_next_byte.wav")
            scp("127.0.0.1", "simon", "/pi_sync",
                sys.argv[2] + "_finnished.txt")
    else:
        print("Invalid device type. <device = 'main'/'sec'>")

except KeyboardInterrupt:
    GPIO.cleanup()

finally:
    GPIO.cleanup()
