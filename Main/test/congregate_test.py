import numpy as np
import pandas as pd
import scipy.constants as constant
import matplotlib.pyplot as plt
# Reads a text file and collects all the data and stores it in an excel file.

def congregate(path, outPath1, outPath2, passTDOA, passPOS, passrate, micPos):

    f = open(path,"r")    
    g = f.readlines()

    fileLen = len(g)

    for i in range(0,fileLen,1):
        g[i] = g[i].strip()
    
    data1 = pd.DataFrame()
    data2 = pd.DataFrame()
    column1 = []
    column2 = []
    column3 = []
    heading = ""
    maxDIS = np.sqrt((0.8**2)+(0.5**2))
    maxTDOA = maxDIS/constant.speed_of_sound
    count = 0
    tdoaPassCount1 = 0
    tdoaPassCount2 = 0
    posPassCount = 0


    for a in g:

        line = a.split(",")
        lineLen = len(line)
        
        if a == '#':
            if not heading == "":

                if tdoaPassCount1 < passrate:
                    column1.append("Fail")
                else:
                    column1.append("Pass")

                if tdoaPassCount2 < passrate:
                    column2.append("Fail")
                else:
                    column2.append("Pass")

                if posPassCount < passrate:
                    column3.append("Fail")
                    column3.append("N/A")
                else:
                    sum = 0
                    for i in column3:
                        if abs(i) <= passPOS:  sum += i
                    avg = sum/posPassCount
                    column3.append("Pass")
                    column3.append(round(avg,2))
                print(column3)    

                data1[heading] = np.array(column1)
                data1[str(count)] = np.array(column2)
                data2[heading] = np.array(column3)

                count += 1
                column1 = []
                column2 = []
                column3 = []
                tdoaPassCount1 = 0
                tdoaPassCount2 = 0
                posPassCount = 0

        elif a != '#' and lineLen == 1:
            heading = a

        elif lineLen == 2: 
            x = float(line[0])
            y = float(line[1])
            actualTdoa_rpi1,actualTdoa_rpi2 = actTDOA(x,y,micPos)

        elif lineLen == 4:
            errorTDOA1 = ((actualTdoa_rpi1-float(line[0]))/maxTDOA)*100
            errorTDOA2 = ((actualTdoa_rpi2-float(line[1]))/maxTDOA)*100
            errorPOS = (np.sqrt((x-float(line[2]))**2+(y-float(line[3]))**2)/maxDIS)*100

            if abs(errorTDOA1) <= passTDOA:  tdoaPassCount1 += 1
            if abs(errorTDOA2) <= passTDOA:  tdoaPassCount2 += 1
            if abs(errorPOS) <= passPOS:  posPassCount += 1

            column1.append(round(errorTDOA1,2))
            column2.append(round(errorTDOA2,2))
            column3.append(round(errorPOS,2))

        else:
            print("invalid Textfile line")
            exit(1)

    column01 = np.array([1,2,3,4,5,6,7,8,9,10,"P/F"])
    column02 = np.array([1,2,3,4,5,6,7,8,9,10,"P/F","AVG"])

    data1.insert(0,"Test No.",column01)
    data2.insert(0,"Test No.",column02)

    data1.to_excel(outPath1)
    data2.to_excel(outPath2)
  

def actTDOA(x,y,micPos):
    d1 = np.sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2)
    d2 = np.sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2)
    d3 = np.sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2)

    actualTdoa_rpi1 = (d1 - d2)/constant.speed_of_sound
    actualTdoa_rpi2 = (d1 - d3)/constant.speed_of_sound

    return actualTdoa_rpi1, actualTdoa_rpi2

def main():
    
    congregate("Main/test/results/positions.csv","Main/test/results/positionsTDOA.xlsx","Main/test/results/positionsPOS.xlsx",10,10,8,[[0.8,0],[0,0],[0.8,0.5]])
    congregate("Main/test/results/sounds.csv","Main/test/results/soundsTDOA.xlsx","Main/test/results/soundsPOS.xlsx",10,10,8,[[0.8,0],[0,0],[0.8,0.5]])
    congregate("Main/test/results/noise.csv","Main/test/results/noiseTDOA.xlsx","Main/test/results/noisePOS.xlsx",10,10,8,[[0.8,0],[0,0],[0.8,0.5]])

    congregate("Main/test/results/positionscat.csv","Main/test/results/positionscatTDOA.xlsx","Main/test/results/positionscatPOS.xlsx",10,10,8,[[0.8,0],[0,0],[0.8,0.5]])


if  __name__ == "__main__":
    main()