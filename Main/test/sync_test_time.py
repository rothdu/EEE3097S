import next_byte
import os

def test(rpi1_ip,rpi1_fin_path,rpi2_fin_path,max):
    results = []
    for i in range(0,max):
        next_byte.delay_test(rpi1_ip, "rpi1")
        next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)

        time1, time2, diff = next_byte.find_delay()

        results.append(diff)
    ave = sum(results)/len(results)
    results.append("###")
    results.append(ave)
    return results

def write_to_file(contents,file_name):
    # Open the file for writing
    with open(file_name, "w") as file:
        # Loop through the array and write each element to the file
        for item in contents:
            file.write(str(item) + "\n")

def main():
    main = os.path.join(os.getcwd(), os.pardir)
    rpi1_fin_path = "rpi1_finnished.txt"
    rpi2_fin_path = "rpi2_finnished.txt"
    rpi1_fin_path = os.path.join(main, rpi1_fin_path)
    rpi2_fin_path = os.path.join(main, rpi2_fin_path)

    results = test("192.168.137.99",rpi1_fin_path,rpi2_fin_path,10)

    write_to_file(results,"sync_time_results.txt")



if __name__ == "__main__":
    main()