import numpy as np
import sympy as sym
import matplotlib.pyplot as plt
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt

#   triangulate(param,mesh):
#   param is an array of the form: [xr,yr,x1,y1,ct1,x2,y2,ct2,x3,y3,ct3]
#
#   xr = X coordinates of reference mic
#   yr = Y coordinates of reference mic
#   x1,x2,x3 = X coordinates of helper mics 1,2,3
#   y1,y2,y3 = Y coordinates of helper mics 1,2,3
#   ct1,ct2,ct3 = Speed constant*TDOA for each mic ref-helper mic pair
#
#   The helper mic coords and constant can be in any order as long as their x, y and ct correspond
#
#   mesh is an array of the form: [xlow, xhigh, xdelta, ylow, yhigh, ydelta]
#
#   Returns xe,ye,x,y,h1,h2,h3: estimated source position, base meshgrid, hyperbolic meshgrid for each mic pair


def triangulate(param, mesh):

    # creates hyperbolic equations in non-linear form
    x, y = sym.symbols('x,y')
    e1 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2) -
                sym.sqrt((x-param[2])**2+(y-param[3])**2), param[4])
    e2 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2) -
                sym.sqrt((x-param[5])**2+(y-param[6])**2), param[7])
    e3 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2) -
                sym.sqrt((x-param[8])**2+(y-param[9])**2), param[10])

    # solves each hyperbolic pair
    ans_arr = [filter_ans(sym.solve([e1, e2]), mesh, x, y),
            filter_ans(sym.solve([e1, e3]), mesh, x, y),
            filter_ans(sym.solve([e2, e3]), mesh, x, y) ]
    # finds midpoint of each pair
    xe = 0
    ye = 0

    success = False
    for ans in ans_arr:
        
        if len(ans) > 0:
            success = True
            xe = xe + ans[0][x]
            ye = ye + ans[0][y]
    xe /= len(ans_arr)
    ye /= len(ans_arr)

    if not success:
        xe = -10
        ye = -10
        
    # defines a meshgrid of x and y, to produce meshgrids h1, h2, h3 for plotting
    x, y = meshgrid(arange(mesh[0], mesh[1], mesh[2]),
                    arange(mesh[3], mesh[4], mesh[5]))
    h1 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[2])**2+(y-param[3])**2)-param[4]
    h2 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[5])**2+(y-param[6])**2)-param[7]
    h3 = sqrt((x-param[0])**2+(y-param[1])**2) - \
        sqrt((x-param[8])**2+(y-param[9])**2)-param[10]

    return sym.N(xe), sym.N(ye), x, y, h1, h2, h3


def filter_ans(ans, mesh, x, y):
    
    
    ans_out = []
    for i in range(len(ans)):  # loop over possible answers

        # check for (invalid) complex answers
        if np.iscomplex(ans[i][x]) or np.iscomplex(ans[i][y]):
            continue
            # check that answer is within range of meshgrid + some tolerance:
        if (ans[i][x] >= mesh[0] and ans[i][x] <= mesh[1]
            and ans[i][y] >= mesh[3] and ans[i][y] <= mesh[4]):
            ans_out.append(ans[i])

    # if you don't find a point inside the grid:
    if len(ans_out) == 0 and len(ans) > 0:
        dists = []
        for i in range(len(ans)):
            if np.iscomplex(ans[i][x]) or np.iscomplex(ans[i][y]):
                continue

            dists.append(compute_closest_distance(ans[i], mesh, x, y))
        
        max_index = np.argmax(dists)
        ans_out.append(ans[max_index])

    return ans_out  


def compute_closest_distance(ans_indexed, mesh, x, y):
    
    dx = np.max(mesh[0] - ans_indexed[x], 0, ans_indexed[x] - mesh[1]) # find dx
    dy = np.min(mesh[3] - ans_indexed[y], 0, ans_indexed[y] - mesh[4]) # find dy
    return np.sqrt(np.power(dx, 2) + np.pow(dy, 2)) # return distance


def dis(x,y,x1,y1,x2,y2,x3,y3,x4,y4):

    d1 = sqrt((x-x1)**2+(y-y1)**2)
    d2 = sqrt((x-x2)**2+(y-y2)**2)
    d3 = sqrt((x-x3)**2+(y-y3)**2)
    d4 = sqrt((x-x4)**2+(y-y4)**2)
    return d1 - d2, d1 - d3, d1 - d4

def distancesize(x): return (x * constant.speed_of_sound)

