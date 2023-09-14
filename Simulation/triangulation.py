import numpy as np
import sympy as sym
import matplotlib.pyplot as plt
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
    ans1 = sym.solve([e1, e2]), mesh, x, y
    ans2 = sym.solve([e1, e3]), mesh, x, y
    ans3 = sym.solve([e2, e3]), mesh, x, y

    # finds midpoint of each pair
    xe = (ans1[x]+ans2[x]+ans3[x])/3
    ye = (ans1[y]+ans2[y]+ans3[y])/3

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
    for i in range(len(ans)):  # loop over possible answers

        # check for (invalid) complex answers
        if np.iscomplex(ans[i][x]) or np.iscomplex(ans[i][y]):
            continue
        # check that answer is within range of meshgrid:
        if (ans[i][x] >= mesh[0] and ans[i][x] <= mesh[1]
                and ans[i][y] >= mesh[3] and ans[i][y] <= mesh[4]):
            return ans[i]
    return None  # no valid result found = return first


def main():
    # sample program for source position 40,40 with mics at corners of 100x100 grid
    # finds the estimated position and plots all the curves and points on one plot
    xs, ys = 40, 40

    t1 = 40*sqrt(2)-20*sqrt(13)
    t2 = 40*sqrt(2)-60*sqrt(2)
    t3 = 40*sqrt(2)-20*sqrt(13)

    param = [0, 0, 0, 100, t1, 100, 100, t2, 100, 0, t3]
    mesh = [0, 100, 1, 0, 100, 1]
    xe, ye, x, y, h1, h2, h3 = triangulate(param, mesh)

    plt.contour(x, y, h1, [0])
    plt.contour(x, y, h2, [0])
    plt.contour(x, y, h3, [0])
    plt.plot(xs, ys, 'co', markersize=10)
    plt.plot(xe, ye, 'r.', markersize=10)
    plt.show()


if __name__ == "__main__":
    main()
