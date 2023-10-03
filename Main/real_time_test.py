import next_byte as next
import Localize as loc
import sys

try:
    while True:
        next.inform_ready("192.168.137.132", "rpi1")
        next.wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")
        print("Transfer finnished")

        x, y = loc.localize("bytes/rpi1_next_byte", "bytes/rpi2_next_byte")
        print("(x,y) = (" + str(x) + "," + str(y) + ")")
except KeyboardInterrupt:
    sys.exit()
