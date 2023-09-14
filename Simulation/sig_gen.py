import numpy as np

import scipy.constants as constant

import matplotlib.pyplot as plt  # for testing


def generate_signal(test_location, mic_location, signal_frequency, sample_frequency=44100, sample_length=10e-3, amplitude=1):


    distance = np.sqrt(np.power(
        test_location[0] - mic_location[0], 2) + np.power(test_location[1] - mic_location[1], 2))
    # distance from test loc to mic loc

    wavelength = constant.speed_of_sound/signal_frequency
    # wavelength of sinusoidal input

    sample_length = (sample_length//wavelength) * wavelength

    time = np.linspace(0, sample_length, int(sample_length*sample_frequency))
    # create signal, initially fill array with time values

    signal = amplitude * np.sin(2*np.pi*signal_frequency*time)


    samples_per_wavelength = sample_frequency/signal_frequency
    sample_offset = int((distance % wavelength) /
                        wavelength * samples_per_wavelength)
    tdoa = sample_offset * 1/sample_frequency
    # phase difference to place in mic location
    #print(signal)
    signal = np.roll(signal, sample_offset)
    #print(signal)
    return signal, tdoa


def signal_to_16_bit(signal, proportion=0.5):

    # find max value of input signal
    max_height = np.max(np.abs(signal))

    # lambda function to convert array
    def convert(x): return (proportion * np.power(2, 15) / max_height) * x

    # convert to realistic range for 16-bit signed integers
    signal = convert(signal)

    # convert to int
    signal.astype(int)

    return signal


def main():

    # create a sample signal and plot it for inspection
    plt.plot(generate_signal((0.9, 0), (0, 0), 1000, 44100, 10e-3, 0.8))
    plt.show()


if __name__ == "__main__":
    main()
