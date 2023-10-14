import numpy as np
import pandas as pd
import scipy.constants as constant
import scipy

def triangulationTest(pos, passPos, micPos):

    data = pd.DataFrame()
    column1 = []
    column2 = []
    column3 = []
    column4 = []

    maxDIS = np.sqrt((0.8**2)+(0.5**2))

    for p in pos:

        d1 = np.sqrt((p[0]-micPos[0][0])**2+(p[1]-micPos[0][1])**2)
        d2 = np.sqrt((p[0]-micPos[1][0])**2+(p[1]-micPos[1][1])**2)
        d3 = np.sqrt((p[0]-micPos[2][0])**2+(p[1]-micPos[2][1])**2)

        actualTdoa_rpi1 = (d1 - d2)/constant.speed_of_sound
        actualTdoa_rpi2 = (d1 - d3)/constant.speed_of_sound
        print(actualTdoa_rpi1)
        print(actualTdoa_rpi2)

        def function(variables):
            (x, y) = variables
            e1 = np.sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - np.sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2) - \
                (actualTdoa_rpi1*constant.speed_of_sound)
            e2 = np.sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - np.sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2) - \
                (actualTdoa_rpi2*constant.speed_of_sound)
            return [e1, e2]

        ans_arr = scipy.optimize.fsolve(function, (0.4, 0.25))

        column1.append(str(p[0]) + "," + str(p[1]))
        column2.append(str(ans_arr[0]) + "," + str(ans_arr[1]))
        
        errorPOS = (np.sqrt((p[0]-ans_arr[0])**2+(p[1]-ans_arr[1])**2)/maxDIS)*100

        column3.append(errorPOS)

        if abs(errorPOS) > passPos:
            column4.append("Fail")
        else:
            column4.append("Pass")

    data["Test Pos"] = np.array(column1)
    data["Estimated Pos"] = np.array(column2)
    data["Percentage Error"] = np.array(column3)    
    data["Pass/Fail"] = np.array(column4)    

    data.to_excel("Main/triTest.xlsx")

def main():
    triangulationTest([[0.5,0.2]],5,[[0.8,0],[0,0],[0.8,0.5]])

if  __name__ == "__main__":
    main()