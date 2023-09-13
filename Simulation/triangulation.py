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
#   mesh is an array of the form: [delta, xlow, xhigh, ylow, yhigh]
# 
#   Returns xe,ye,x,y,h1,h2,h3: estimated source position, base meshgrid, hyperbolic meshgrid for each mic pair

def triangulate(param,mesh):

    # creates hyperbolic equations in non-linear form
    x,y = sym.symbols('x,y')
    e1 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[2])**2+(y-param[3])**2),param[4])
    e2 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[5])**2+(y-param[6])**2),param[7])
    e3 = sym.Eq(sym.sqrt((x-param[0])**2+(y-param[1])**2)-sym.sqrt((x-param[8])**2+(y-param[9])**2),param[10])

    # solves each hyperbolic pair
    ans1 = sym.solve([e1,e2])
    ans2 = sym.solve([e1,e3])
    ans3 = sym.solve([e2,e3])

    # finds midpoint of each pair
    xe = (ans1[0][x]+ans2[0][x]+ans3[0][x])/3
    ye = (ans1[0][y]+ans2[0][y]+ans3[0][y])/3

    # defines a meshgrid of x and y, to produce meshgrids h1, h2, h3 for plotting
    x, y = meshgrid( arange(mesh[1], mesh[2], mesh[0]), arange(mesh[3], mesh[4], mesh[0]))
    h1 = sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[2])**2+(y-param[3])**2)-param[4]
    h2 = sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[5])**2+(y-param[6])**2)-param[7]
    h3 = sqrt((x-param[0])**2+(y-param[1])**2)-sqrt((x-param[8])**2+(y-param[9])**2)-param[10]

    return sym.N(xe) , sym.N(ye), x, y, h1, h2, h3 

def main():
    # sample program for source position 40,40 with mics at corners of 100x100 grid
    # finds the estimated position and plots all the curves and points on one plot
    xs, ys = 40, 40
    
    t1 = 40*sqrt(2)-20*sqrt(13)
    t2 = 40*sqrt(2)-60*sqrt(2)
    t3 = 40*sqrt(2)-20*sqrt(13)

    param = [0,0,0,100,t1,100,100,t2,100,0,t3]
    xe, ye, x, y, h1, h2, h3 = triangulate(param)
    
    plt.contour(x,y,h1,[0])
    plt.contour(x,y,h2,[0])
    plt.contour(x,y,h3,[0])
    plt.plot(xs,ys,'co',markersize=10)
    plt.plot(xe,ye,'r.',markersize=10)
    plt.show()

if __name__ == "__main__":
    main()