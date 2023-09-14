import numpy as np

import matplotlib.pyplot as plt
import pyroomacoustics
import signal_procesing
from scipy.io import wavfile
import scipy.constants as constant
import os


def gen_delay(test_location, mic_location, signal_frequency, sample_frequency, sample_length):

    distance = np.sqrt(np.power(
        test_location[0] - mic_location[0], 2) + np.power(test_location[1] - mic_location[1], 2))
    # distance from test loc to mic loc

    wavelength = constant.speed_of_sound/signal_frequency
    # wavelength of sinusoidal input

    samples_per_period = sample_frequency/signal_frequency
    period = 1/signal_frequency

    num_periods = int(sample_length//period + 1)

    sample_length = num_periods * samples_per_period / sample_frequency

    # create signal, initially fill array with time values

    samples_per_wavelength = sample_frequency/signal_frequency
    sample_offset = int((distance % wavelength) /
                        wavelength * samples_per_wavelength)
    tdoa = sample_offset * 1/sample_frequency

    signal = signal[sample_offset, sample_length]
    # print(signal)
    return signal, tdoa


def load_signal(path):
    s_r, sig = wavfile.read(path)
    return s_r, sig[:, 0]


def main():

    sample_rate, ref_sig = load_signal("sound.wav")


if __name__ == "__main__":
    main()
