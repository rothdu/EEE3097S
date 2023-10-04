import os
import time
import subprocess


def inform_ready(pi_ip, pi_name):
    source_file = "Main/pc_ready.txt"
    destination_host = pi_name + "@" + pi_ip + ":/home/" + pi_name

    # Construct the scp command
    scp_command = ["scp", source_file, destination_host]
    subprocess.run(scp_command)


def delay_test(pi_ip, pi_name):
    source_file = "Main/test_ready.txt"
    destination_host = pi_name + "@" + pi_ip + ":/home/" + pi_name

    # Construct the scp command
    scp_command = ["scp", source_file, destination_host]
    subprocess.run(scp_command)


def wait_trans(rpi1_fin_path, rpi2_fin_path):
    while not (os.path.exists(rpi1_fin_path) and os.path.exists(rpi2_fin_path)):
        time.sleep(0.000001)
    os.remove(rpi1_fin_path)
    os.remove(rpi2_fin_path)


def find_delay():
    with open("Main/bytes/rpi1_time.txt", 'r') as file:
        # Read the entire contents of the file into a string
        time_1 = float(file.read())

    with open("Main/bytes/rpi2_time.txt", 'r') as file:
        # Read the entire contents of the file into a string
        time_2 = float(file.read())

    return time_2-time_1


def main():
    # Your main script logic here
    for i in range(0, 20):
        delay_test("192.168.137.132", "rpi1")
        wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")
        print("Transfer finnished")
        print(find_delay())


if __name__ == "__main__":
    main()
