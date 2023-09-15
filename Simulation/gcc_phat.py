"""
 Estimate time delay using GCC-PHAT 
 Copyright (c) 2017 Yihui Xiong

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

# obtained from https://github.com/xiongyihui/tdoa/blob/master/gcc_phat.py

import numpy as np

import matplotlib.pyplot as plt

def gcc_phat_2(signal1, signal2, fs):


    n = (signal2.shape[0] + signal1.shape[0])
    fft_signal_1 = np.fft.rfft(signal1, n=n)
    fft_signal_2 = np.fft.rfft(signal2, n=n)
    R = fft_signal_2 * np.conj(fft_signal_1)
    phat = R / np.abs(R)
    cc = np.fft.irfft(phat, n=n)

    max_index = np.argmax(cc)

    tdoa = max_index/fs


    ##### test plots
    """
    fig1 = plt.figure(1)

    ax1 = fig1.add_subplot()

    
    ax1.plot(signal1)
    ax1.plot(signal2)

    fig2 = plt.figure(2)

    ax2, ax3 = fig2.subplots(2, 1)
    ax2.plot(np.abs(fft_signal_1))
    ax2.plot(np.abs(fft_signal_2))

    ax3.plot(np.angle(fft_signal_1))
    ax3.plot(np.angle(fft_signal_2))


    fig3 = plt.figure(3)
    ax4, ax5 = fig3.subplots(2, 1)

    ax4.plot(np.abs(R))
    ax5.plot(np.angle(R))

    fig4 = plt.figure(4)
    ax6, ax7 = fig4.subplots(2, 1)

    ax6.plot(np.abs(phat))
    ax7.plot(np.angle(phat))

    fig5 = plt.figure(5)

    ax8 = fig5.add_subplot()

    ax8.plot(cc)

    plt.show()
    plt.close()

    """


    return tdoa



def gcc_phat_gpt(signal1, signal2, fs):
    # Ensure both input signals have the same length
    assert len(signal1) == len(signal2), "Input signals must have the same length"

    n = 4* len(signal1)

    # Perform GCC-PHAT cross-correlation
    X = np.fft.rfft(signal1, n)
    Y = np.fft.rfft(signal2, n)
    R = X * np.conj(Y)

    ### tests
    plt.plot(signal1)
    plt.plot(signal2)
    plt.savefig("testplots/test1")
    plt.close()


    plt.plot(X)
    plt.plot(Y)
    plt.savefig("testplots/test2")
    plt.close()

    plt.plot(np.abs(R))
    plt.savefig("testplots/test3")
    plt.close()


    ### end tests

    # Calculate phase transform
    R /= np.abs(R)

    # Calculate the cross-correlation
    r = np.fft.irfft(R)

    ### more tests

    plt.plot(np.abs(r))
    plt.savefig("testplots/test4")
    plt.close()

    # Find the index of the maximum value (time delay)
    max_index = np.argmax(np.abs(r))

    # Calculate TDOA in seconds
    tdoa = max_index / fs

    return tdoa


def gcc_phat(sig, refsig, fs=44100, max_tau=None, interp=16):
    '''
    This function computes the offset between the signal sig and the reference signal refsig
    using the Generalized Cross Correlation - Phase Transform (GCC-PHAT)method.
    '''
    
    # make sure the length for the FFT is larger or equal than len(sig) + len(refsig)
    n = sig.shape[0] + refsig.shape[0]

    # Generalized Cross Correlation Phase Transform
    SIG = np.fft.rfft(sig, n=n)
    REFSIG = np.fft.rfft(refsig, n=n)
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
    
    refsig = np.linspace(1, 10, 10)

    for i in range(0, 10):
        sig = np.concatenate((np.linspace(0, 0, i), refsig, np.linspace(0, 0, 10 - i)))
        offset, b = gcc_phat(sig, refsig)
        print(offset)


if __name__ == "__main__":
    main()




