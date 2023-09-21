import scipy.optimize
import scipy.constants as constant
import numpy as np
from numpy import arange, meshgrid, sqrt
import time
import matplotlib.pyplot as plt

def dis(x,y,x1,y1,x2,y2,x3,y3,x4,y4):

    d1 = sqrt((x-x1)**2+(y-y1)**2)
    d2 = sqrt((x-x2)**2+(y-y2)**2)
    d3 = sqrt((x-x3)**2+(y-y3)**2)
    d4 = sqrt((x-x4)**2+(y-y4)**2)
    return d1 - d2, d1 - d3, d1 - d4

def distancesize(x): return (x * constant.speed_of_sound)

def triangulate(param,mesh):

    def fun1(variables):
        (x,y)= variables
        e1 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[2])**2+(y-param[3])**2) - param[4]
        e2 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[5])**2+(y-param[6])**2) - param[7]
        return [e1,e2]
    
    def fun2(variables):
        (x,y)= variables
        e1 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[2])**2+(y-param[3])**2) - param[4]
        e3 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[8])**2+(y-param[9])**2) - param[10]
        return [e1,e3]
    
    def fun3(variables):
        (x,y)= variables
        e2 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[5])**2+(y-param[6])**2) - param[7]
        e3 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[8])**2+(y-param[9])**2) - param[10]
        return [e2,e3]

    # ans_arr = [filter_ans(scipy.optimize.fsolve(fun1, (0, 0)), mesh),
    #         filter_ans(scipy.optimize.fsolve(fun2, (0, 0)), mesh),
    #         filter_ans(scipy.optimize.fsolve(fun3, (0, 0)), mesh) ]
    ans_arr = [scipy.optimize.fsolve(fun1, (0, 0)),
            scipy.optimize.fsolve(fun2, (0, 0)),
            scipy.optimize.fsolve(fun3, (0, 0))]

    ans_arr = filter_ans(ans_arr)
    # finds midpoint of each pair
    xe = 0
    ye = 0
    numAns = len(ans_arr)

    if numAns > 0:

        for ans in ans_arr:
            xe += ans[0]
            ye += ans[1]

        xe /= numAns
        ye /= numAns
    else:
        xe = -10
        ye = -10
        
    # defines a meshgrid of x and y, to produce meshgrids h1, h2, h3 for plotting
    x, y = meshgrid(arange(mesh[0], mesh[1], mesh[2]),
                    arange(mesh[3], mesh[4], mesh[5]))
    # x, y = meshgrid(arange(-0.5, 1.5, 2/100),
    #                 arange(-0.05, 1.5, 2/100))
    h1 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[2])**2+(y-param[3])**2)-param[4]
    h2 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[5])**2+(y-param[6])**2)-param[7]
    h3 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[8])**2+(y-param[9])**2)-param[10]


    return xe, ye, x, y, h1, h2, h3

def filter_ans(ans):

    ans_out = []
    for i in range(len(ans)):  # loop over possible answers

        # check for (invalid) complex answers
        if (not isinstance(ans[i][0],complex) and not isinstance(ans[i][1],complex)):
            ans_out.append(ans[i])

    # if you don't find a point inside the grid:
    # if len(ans_out) == 0 and len(ans) > 0:
    #     try:
    #         if (len(ans) == 2) and (ans[0][0] == ans[1][0]):
    #             if ans[0][1] >= 0:
    #                 ans_out.append(ans[0])
    #                 return ans_out
    #             elif ans[1][1] >= 0:
    #                 ans_out.append(ans[1])
    #                 return ans_out
    #     except TypeError:
    #         print("Caught error with complex value")

    #     dists = []
    #     for i in range(len(ans)):
    #         try:
    #             if ans[i][0] > 0 or True:
    #                 dists.append(compute_closest_distance(ans[i], mesh, x, y))
    #         except TypeError:
    #             continue

    #     if len(dists) != 0:
    #         max_index = np.argmax(dists)
    #         ans_out.append(ans[max_index])
    # debug
    # print(ans)
    # print(ans_out)
    return ans_out  

def compute_closest_distance(ans_indexed, mesh, x, y):
    
    dx = np.max([mesh[0] - ans_indexed[x], 0, ans_indexed[x] - mesh[1]]) # find dx
    dy = np.min([mesh[3] - ans_indexed[y], 0, ans_indexed[y] - mesh[4]]) # find dy
    return np.power((np.power(dx, 2) + np.power(dy, 2)), 0.5) # return distance

def main():
    xs, ys = 0.7988246329861778, 0.12506774017562355
    d1,d2,d3 = dis(xs,ys,0,0,0.8,0,0.8,0.5,0,0.5)

    tdoa1 = d1/constant.speed_of_sound
    tdoa2 = d2/constant.speed_of_sound
    tdoa3 = d3/constant.speed_of_sound

    tdoa = [tdoa1, tdoa2, tdoa3]
    print(tdoa)

    # t1,t2,t3 = 0.002018140589569161, 0.0012698412698412698, -0.00020408163265306123
    # d1 = distancesize(t1)
    # d2 = distancesize(t2)
    # d3 = distancesize(t3)

    param = [0, 0, 0.8, 0, d1, 0.8, 0.5, d2, 0, 0.5, d3]
    mesh = [0, 0.8, 0.8/100, 0, 0.5, 0.5/100]
    
    start_time = time.time()
    
    xe, ye, x, y, h1, h2, h3 = triangulate(param, mesh)
    end_time = time.time()

    print(xe)
    print(ye)

    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time) 

    plt.contour(x, y, h1, [0])
    plt.contour(x, y, h2, [0])
    plt.contour(x, y, h3, [0])
    plt.plot(xs, ys, 'co', markersize=10)
    plt.plot(xe, ye, 'r.', markersize=10)
    plt.show()

if __name__ == "__main__":
    main()