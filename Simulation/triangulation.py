import numpy as np
import sympy as sym
import matplotlib.pyplot as plt
from numpy import arange, meshgrid, sqrt

#   triangulate(param):
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
#   Returns and xe and ye of the estimated source position.

def triangulate(param):

    x,y = sym.symbols('x,y')
    e1 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[2])**2+(y-param[3])**2),param[4])
    e2 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[5])**2+(y-param[6])**2),param[7])
    e3 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[8])**2+(y-param[9])**2),param[10])

    ans1 = sym.solve([e1,e2])
    ans2 = sym.solve([e1,e3])
    ans3 = sym.solve([e2,e3])

    xe = (ans1[0][x]+ans2[0][x]+ans3[0][x])/3
    ye = (ans1[0][y]+ans2[0][y]+ans3[0][y])/3

    return sym.N(xe) , sym.N(ye)

def plotgen(xs,xe,param):

    delta = 1
    x, y = meshgrid( arange(0, 100, delta), arange(0, 100, delta))
    plt.contour(x,y, sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[2])**2+(y-param[3])**2)-param[4],[0])
    plt.contour(x,y, sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[5])**2+(y-param[6])**2)-param[7],[0])
    plt.contour(x,y, sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[8])**2+(y-param[9])**2)-param[10],[0])
    
    plt.plot(xs[0],xs[1],'co',markersize=10)
    plt.plot(xe[0],xe[1],'r.',markersize=10)
    
    plt.show()

def main():
    t1 = 40*sqrt(2)-20*sqrt(13)
    t2 = 40*sqrt(2)-60*sqrt(2)
    t3 = 40*sqrt(2)-20*sqrt(13)

    param = [0,0,0,100,t1,100,100,t2,100,0,t3]
    x, y = triangulate(param)
    plotgen([40,40],[x,y],param)

if __name__ == "__main__":
    main()