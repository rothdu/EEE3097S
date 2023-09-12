import numpy as np

import scipy.constants as constant

import matplotlib.pyplot as plt # for testing

def generate_signal(test_location, mic_location, signal_frequency, sample_frequency, sample_length, amplitude):

    distance = np.sqrt(np.power(test_location[0] - mic_location[0], 2) + np.power(test_location[1] - mic_location[1], 2))
    # distance from test loc to mic loc

    wavelength = constant.speed_of_sound/signal_frequency
    # wavelength of sinusoidal input

    phase_offset = (distance%wavelength)/wavelength*2*np.pi
    # phase difference to place in mic location

    signal = np.linspace(0, sample_length, int(sample_length*sample_frequency))
    # create signal, initially fill array with time values

    siggen = lambda t: amplitude * np.power(2,15) * np.sin(2*np.pi*signal_frequency*t - phase_offset)
    # lambda function to populate array

    signal = siggen(signal)
    # generate sinusoidal signal

    signal.astype(int)
    # convert to int

    return signal

def main():

    # create a sample signal and plot it for inspection
    plt.plot(generate_signal((0.9, 0), (0, 0), 1000, 44100, 10e-3, 0.8))
    plt.show()


if __name__ == "__main__":
    main()

    

