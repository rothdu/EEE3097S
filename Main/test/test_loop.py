# a program to run a loop of tests and output to a text file

import localize as loc
import next_byte
import time

# some useful global variables
plotSize = (640, 480)
samplingPeriod = 1

micPositions = [[0, 0.5], [0.8, 0.5], [0, 0]]

rpi1_fin_path = "Main/rpi1_finnished.txt"
rpi2_fin_path = "Main/rpi2_finnished.txt"

rpi1_byte_path = "Main/bytes/rpi1_next_byte.wav"
rpi2_byte_path = "Main/bytes/rpi2_next_byte.wav"

rpi1_ip = "192.168.137.99"

mode = "continuous"



def runTest(startTime):
    next_byte.inform_ready(rpi1_ip, "rpi1")
    if (next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)):
        result = loc.localize(rpi1_byte_path,
                                rpi2_byte_path, micPositions, startTime,
                                hyperbola=True, refTDOA=True)

    else:
        result = {
            "result": [],
            "hyperbola": [],
            "tdoa": [],
            "reftdoa": [],
            "times": [startTime],
            "errorMessage": ["Failed to acquire signal"]
            }
    
    return result


def nTests(n, fileName):
    outFile = open("tests/results/" + fileName + ".csv", "a", encoding="utf-8")

    while True:
        try:
            header = input("Test Header: ")
            x = promptForFloat("Enter position x: ")
            y = promptForFloat("Enter position y: ")

            outFile.write("#" + "\n")
            outFile.write(header + "\n")
            outFile.write(str(x) + "," + str(y) + "\n")

            for i in range(n):
                
                input("Click enter to start next test")

                result = runTest(time.time())

                if len(result['result'] != 0):

                    outFile.write(str(result["tdoa"][0]) + "," + str(result["tdoa"][1]) + "," + str(result["result"][0]) + "," + str(result["result"][1]) + "\n")
                else:
                    outFile.write(result["errorMessage"][0] + "\n")
        except KeyboardInterrupt:
            print("Ending testing loop")
            break 


def contTests(fileName):
    outFile = open("tests/results/" + fileName + ".csv", "w", encoding="utf-8")

    while True:
        try:
        
            input("Click enter to start next test")

            result = runTest(time.time())

            updateTime = time.time() - result['times'][0]

            if len(result['result'] != 0):

                outFile.write(str(result["tdoa"][0]) + "," + str(result["tdoa"][1]) + "," + str(result["result"][0]) + "," + str(result["result"][1]) + "," + str(updateTime) + "\n" )
            else:
                outFile.write(result["errorMessage"][0] + "\n")
        except KeyboardInterrupt:
            print("Ending testing loop")
            break 



def promptForInt(promptText):
    while True:
        try:
            return int(input(promptText))
        except ValueError:
            print("Invalid input")
            continue

def promptForFloat(promptText):
    while True:
        try:
            return float(input(promptText))
        except ValueError:
            print("Invalid input")
            continue




def main():

    welcomeString = "\
        Modes:\n\
        1: Run n tests in a row, output to txt\n\
        2: Run tests continuously until prompted to stop, output to txt\n\
        q: Quit\
        "

    print(welcomeString)
    
    
    while (True):
        print(welcomeString)
        inpt = input()

        if inpt == '1':
            
            n = promptForInt("Enter number of tests: ")
            fileName = input("File name (no path or extension): ")


            nTests(n, fileName)
        
        if inpt == '2':
            fileName = input("File name (no path or extension): ")

            contTests(fileName)

        
        elif inpt.casefold() == 'q':
            print("Goodbye")
            break
        
        else:
            print("Invalid input entered")


if __name__ == "__main__":
    main()