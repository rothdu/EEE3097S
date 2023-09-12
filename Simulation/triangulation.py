import numpy as np
from sympy.plotting import plot
import sympy as sym

#   triangulate(x1,y1,x2,y2,ct):
#
#   xr = [xr,xr,xr] X coordinates of reference mic
#   yr = [yr,yr,yr] Y coordinates of reference mic
#   xh = [x1,x2,x3] X coordinates of helper mics 1,2,3
#   yh = [y1,y2,y3] Y coordinates of helper mics 1,2,3
#   ct = [ct1,ct2,ct3] Speed constant*TDOA for each mic ref-helper mic pair
#   The helper mic coords and constant can be in any order as long as their x, y and ct correspond
#   
#   Returns and x and y of the estimated source position.

def triangulate(x1,y1,x2,y2,ct):

    x,y = sym.symbols('x,y')
    e1 = sym.Eq(sym.sqrt((x-x1[0])**2+(y-y1[0])**2)-sym.sqrt((x-x2[0])**2+(y-y2[0])**2),ct[0])
    e2 = sym.Eq(sym.sqrt((x-x1[1])**2+(y-y1[1])**2)-sym.sqrt((x-x2[1])**2+(y-y2[1])**2),ct[1])
    e3 = sym.Eq(sym.sqrt((x-x1[2])**2+(y-y1[2])**2)-sym.sqrt((x-x2[2])**2+(y-y2[2])**2),ct[2])

    ans1 = sym.solve([e1,e2])
    ans2 = sym.solve([e1,e3])
    ans3 = sym.solve([e2,e3])

    xs = (ans1[0][x]+ans2[0][x]+ans3[0][x])/3
    ys = (ans1[0][y]+ans2[0][y]+ans3[0][y])/3

    # print(ans1)
    # print(ans2)
    # print(ans3)
    # print(sym.N(xs))
    # print(sym.N(ys))

    return sym.N(xs) , sym.N(ys)

