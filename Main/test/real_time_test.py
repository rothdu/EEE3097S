import next_byte
import Main.localize as loc
import sys

try:
    while True:
        next_byte.inform_ready("192.168.137.132", "rpi1")
        next_byte.wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")

        x, y = loc.localize("Main/bytes/rpi1_next_byte.wav",
                            "Main/bytes/rpi2_next_byte.wav", False)
        print("(x,y) = (" + str(x) + "," + str(y) + ")")
except KeyboardInterrupt:
    sys.exit()
