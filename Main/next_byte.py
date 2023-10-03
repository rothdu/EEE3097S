import os
import time
import subprocess


def inform_ready(pi_ip, pi_name):
    source_file = "Main/pc_ready.txt"
    destination_host = pi_name + "@" + pi_ip + ":/home/" + pi_name

    # Construct the scp command
    scp_command = ["scp", source_file, destination_host]
    subprocess.run(scp_command)


def wait_trans(rpi1_fin_path, rpi2_fin_path):
    while not (os.path.exists(rpi1_fin_path) and os.path.exists(rpi2_fin_path)):
        time.sleep(0.000001)
    os.remove(rpi1_fin_path)
    os.remove(rpi2_fin_path)


def main():
    # Your main script logic here
    inform_ready("192.168.137.132", "rpi1")
    wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")
    print("Transfer finnished")


if __name__ == "__main__":
    main()
