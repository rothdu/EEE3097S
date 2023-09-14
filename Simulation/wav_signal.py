import numpy as np

import matplotlib.pyplot as plt
import pyroomacoustics
import signal_procesing
from scipy.io import wavfile
import scipy.constants as constant
import os


def gen_delay(signal, test_location, mic_location, signal_frequency, sample_frequency, n_samples):
    distance = np.sqrt(np.power(
        test_location[0] - mic_location[0], 2) + np.power(test_location[1] - mic_location[1], 2))
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

    sig, tdoa = gen_delay(ref_sig, [0.0, 0.4], [
                          0.0, 0.0], 250, sample_rate, 1000)

    plt.plot(ref_sig[0:1000])
    plt.plot(sig)
    plt.show()

    print(tdoa)


if __name__ == "__main__":
    main()
