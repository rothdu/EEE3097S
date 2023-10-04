# a file of functions used to test individual subsystems

import next_byte

def signalAcquisitionTest():
    next_byte.inform_ready("192.168.137.132", "rpi1")
    next_byte.wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")
