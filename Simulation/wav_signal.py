import numpy as np

import matplotlib.pyplot as plt
import signal_procesing
from scipy.io import wavfile
import scipy.constants as constant
import os
import gcc_phat
import triangulation


def gen_delay(signal, test_location, mic_location, signal_frequency, sample_frequency, n_samples):
    distance = np.sqrt((test_location[0] - mic_location[0])**2 + (test_location[1] - mic_location[1])**2)
    # distance from test loc to mic loc

    # wavelength = constant.speed_of_sound/signal_frequency
    # wavelength of sinusoidal input

    # samples_per_period = sample_frequency/signal_frequency
    # period = 1/signal_frequency

    # create signal, initially fill array with time values

    # samples_per_wavelength = sample_frequency/signal_frequency
    # sample_offset = int((distance % wavelength) /
    #                     wavelength * samples_per_wavelength)
    # tdoa = sample_offset * 1/sample_frequency

    tdoa = distance/constant.speed_of_sound
    sample_offset = int(tdoa // (1/sample_frequency))

    zeros = np.zeros(sample_offset)
    signal = np.concatenate((zeros, signal))

    signal = signal[0: n_samples]
    # print(signal)
    return signal, tdoa


def load_signal(path):
    s_r, sig = wavfile.read(path)
    return s_r, sig[:, 0]


def main():

    sample_rate, ref_sig = load_signal("Simulation/sound.wav")

    xs, ys = 0.6,0.3
    sig1, tdoa1 = gen_delay(ref_sig, [xs, ys], [
                          0.0, 0.0], 250, sample_rate, 1000)
    sig2, tdoa2 = gen_delay(ref_sig, [xs, ys], [
                          0.8, 0.0], 250, sample_rate, 1000)
    sig3, tdoa3 = gen_delay(ref_sig, [xs, ys], [
                          0.8, 0.5], 250, sample_rate, 1000)
    sig4, tdoa4 = gen_delay(ref_sig, [xs, ys], [
                          0.0, 0.5], 250, sample_rate, 1000)
    
    tdoa = [tdoa1-tdoa2, tdoa1 - tdoa3, tdoa1-tdoa4]
    print(tdoa)

    tau1 = gcc_phat.gcc_phat(sig1,sig2,sample_rate)
    tau2 = gcc_phat.gcc_phat(sig1,sig3,sample_rate)
    tau3 = gcc_phat.gcc_phat(sig1,sig4,sample_rate)

    tau = [tau1, tau2, tau3]
    print(tau)

    # d1 = tdoa[0]*constant.speed_of_sound
    # d2 = tdoa[1]*constant.speed_of_sound
    # d3 = tdoa[2]*constant.speed_of_sound

    d1 = tau[0]*constant.speed_of_sound
    d2 = tau[1]*constant.speed_of_sound
    d3 = tau[2]*constant.speed_of_sound

    param = [0, 0, 0.8, 0, d1, 0.8, 0.5, d2, 0, 0.5, d3]
    mesh = [-0.5, 1.5, 2/100, -0.5, 1.5, 2/100]
    xe, ye, x, y, h1, h2, h3 = triangulation.triangulate(param, mesh)

    print(xe)
    print(ye)

    plt.contour(x, y, h1, [0])
    plt.contour(x, y, h2, [0])
    plt.contour(x, y, h3, [0])
    plt.plot(xs, ys, 'co', markersize=10)
    plt.plot(xe, ye, 'r.', markersize=10)
    plt.show()
    # plt.plot(ref_sig[0:50])
    # plt.plot(sig1)
    # plt.plot(sig2)
    # plt.show()

if __name__ == "__main__":
    main()
