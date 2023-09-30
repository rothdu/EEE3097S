from scipy.io import wavfile
import numpy as np
import scipy.optimize
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt
import time
import matplotlib.pyplot as plt

def localize(path1,path2,hyperbola = "False"):
    SR, sig1 = wavfile.read(path1)
    SR, sig2 = wavfile.read(path2)

    L1 = sig1[:,0]
    R1 = sig1[0,:] 
    L2 = sig2[:,0] 
    R2 = sig2[0,:]

    tdoa1 = gcc_phat(L1,R1,SR)
    tdoa2 = gcc_phat(L1,L2,SR)
    tdoa3 = gcc_phat(L1,R2,SR)

    def fun1(variables):
        (x,y)= variables
        e1 = sqrt((x)**2+(y)**2) - sqrt((x-0.8)**2+(y)**2) - (tdoa1*constant.speed_of_sound)
        e2 = sqrt((x)**2+(y)**2) - sqrt((x)**2+(y-0.5)**2) - (tdoa1*constant.speed_of_sound)
        return [e1,e2]
    
    def fun2(variables):
        (x,y)= variables
        e1 = sqrt((x)**2+(y)**2) - sqrt((x-param[2])**2+(y-param[3])**2) - (tdoa1*constant.speed_of_sound)
        e3 = sqrt((x)**2+(y)**2) - sqrt((x-param[8])**2+(y-param[9])**2) - (tdoa1*constant.speed_of_sound)
        return [e1,e3]
    
    def fun3(variables):
        (x,y)= variables
        e2 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[5])**2+(y-param[6])**2) - (tdoa1*constant.speed_of_sound)
        e3 = sqrt((x-param[0])**2+(y-param[1])**2) - sqrt((x-param[8])**2+(y-param[9])**2) - (tdoa1*constant.speed_of_sound)
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


def gcc_phat(refsig, sig, fs, max_tau=None, interp=16):
    '''
    This function computes the offset between the signal sig and the reference signal refsig
    using the Generalized Cross Correlation - Phase Transform (GCC-PHAT)method.
    '''
    
    # make sure the length for the FFT is larger or equal than len(sig) + len(refsig)
    n = refsig.shape[0] + sig.shape[0]

    # Generalized Cross Correlation Phase Transform
    REFSIG = np.fft.rfft(refsig, n=n)
    SIG = np.fft.rfft(sig, n=n)
    R = SIG * np.conj(REFSIG)

    cc = np.fft.irfft((R/np.abs(R)), n=(interp * n))

    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)

    cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))

    # find max cross correlation index
    shift = np.argmax(np.abs(cc)) - max_shift

    tau = shift / float(interp * fs)
    
    return tau    
    

def main():
     x, y = localize("rpi1_next_byte.wav","rpi2_next_byte.wav")
    

if __name__ == "__main__":
    main()
