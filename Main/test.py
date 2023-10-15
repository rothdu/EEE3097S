import scipy.constants as constant
from numpy import sqrt, arange, meshgrid
import matplotlib.pyplot as plt
import numpy as np


def genHyperbola(micPos, tdoa_rpi1, tdoa_rpi2):
    # defines a meshgrid of x and y, to produce meshgrids h_rpi1_test, h_rpi2_test for plotting
    x, y = meshgrid(arange(0, 0.8+0.8/100, 0.8/100), arange(-(0.5+0.5/100), 0.5+0.5/100, 0.5/100))
    # testing rpi 1
    h_rpi1_test = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2) - \
        (tdoa_rpi1*constant.speed_of_sound)
    h_rpi2_test = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2) - \
        (tdoa_rpi2*constant.speed_of_sound)

    return [x, y, h_rpi1_test, h_rpi2_test]

def main():
    X, Y, h1, h2 = genHyperbola([[0,0],[0.8,0],[0.8,0]], -0.001, 0.001)
    # Create a subplot with 1 row and 2 columns
    plt.contour(X, Y, h1, [0], color='k')
    plt.text(0.17, 0.4, '-1ms', fontsize=12, color='k')
    plt.text(0.55, 0.4, '+1ms', fontsize=12, color='k')
    plt.text(0.01, 0.05, 'Ref Mic', fontsize=12, color='c')
    plt.text(0.65, 0.05, 'Helper Mic', fontsize=12, color='g')

    plt.contour(X, Y, h2, [0], color='k')
    plt.plot(0,0,marker='o', markersize = 20, color = "c")
    plt.plot(0.8,0,marker='o', markersize = 20, color = "g")
    plt.title('Triangulation: Negative vs Positive TDOA')

    # Adjust layout and display the plot
    plt.show()


    # # Generate data for the hyperbola
    # x = np.linspace(-5, 5, 100)
    # y = np.linspace(-5, 5, 100)
    # X, Y = np.meshgrid(x, y)
    # Z = X**2/4 - Y**2/9  # Equation of a hyperbola

    # # Create a contour plot for the hyperbola
    # plt.contour(X, Y, Z, levels=[1], colors='b')
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.title('Hyperbola')
    # plt.text(1, 2, 'Hyperbola', fontsize=12, color='b')

    # # Display the plot
    # plt.show()


if __name__ == "__main__":
    main()