from scipy.io import wavfile
import numpy as np
import next_byte
import os
from scipy import signal
import matplotlib.pyplot as plt
import localize as loc
import matplotlib.gridspec as gridspec
    
def similarity(actual,recorded):
    # Calculate the correlation coefficient
    correlation_matrix = np.corrcoef(actual, recorded)

    # The correlation coefficient is in the off-diagonal element of the matrix
    correlation_coefficient = correlation_matrix[0, 1]

    return correlation_coefficient

def readSignal(path1, path2):

    # Import Wav files
    SR, rpi1 = wavfile.read(path1)
    SR, rpi2 = wavfile.read(path2)

    # Separate into channels
    rpi1_chan_1 = rpi1[:, 0]
    rpi1_chan_2 = rpi1[:, 1]
    rpi2_chan_1 = rpi2[:, 0]
    rpi2_chan_2 = rpi2[:, 1]

    return SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2

def actual_to_array(actual_file):
    _ , array = wavfile.read(actual_file)
    array = array[:, 0]
    return array


def test_corr(test_file,state, figure_name, figure_save):
    rpi1_wav = "Main/bytes/aqu_sound_1.wav"
    rpi2_wav = "Main/bytes/aqu_sound_2.wav"

    actual = actual_to_array(test_file)
    results = loc.signalAquisitionTest(rpi1_wav, rpi2_wav)
    
    for i in range(0,4):
        results[state][i] = results[state][i][:600000]

    # Create a figure with a grid of subplots
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle(figure_name)

    # Define the grid using gridspec
    gs = gridspec.GridSpec(3, 2, width_ratios=[1, 1], height_ratios=[1, 1, 2])

    # Subplots in the first row
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])

    # Subplots in the second row
    ax3 = plt.subplot(gs[1, 0])
    ax4 = plt.subplot(gs[1, 1])

    # Subplot spanning the entire third row
    ax5 = plt.subplot(gs[2, :])

    # Now, you can plot in each of the subplots as needed
    ax1.plot(results[state][2],color="b")
    ax1.set_title('PI 1 Channel 1')

    ax2.plot(results[state][1],color="g")
    ax2.set_title('PI 1 Channel 1')

    ax3.plot(results[state][2], color="r")
    ax3.set_title('PI 2 Channel 1')

    ax4.plot(results[state][3], color="m")
    ax4.set_title('PI 2 Channel 2')

    ax5.plot(actual, color="y")
    ax5.set_title('Source Signal')

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the figure
    plt.savefig(figure_save, format='jpg')
    plt.show()
    plt.close()

def test_size():
    rpi1_wav = "Main/bytes/aqu_sound_1.wav"
    rpi2_wav = "Main/bytes/aqu_sound_2.wav"
    
    SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = readSignal(
        rpi1_wav, rpi2_wav)
    
    lengths = [len(rpi1_chan_1), len(rpi1_chan_2), len(rpi2_chan_1), len(rpi2_chan_2)]

    if all(length == lengths[0] for length in lengths):
        result = True
    else:
        result = False

    return result

def processSignal(rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2):

    # Define the cutoff frequency (in Hz)
    cutoff_frequency = 200.0
    low_cut = 200
    high_cut = 20000

    # Normalize the cutoff frequency by the Nyquist frequency
    nyquist = 0.5 * 44100
    cutoff_frequency /= nyquist
    low_cut /= nyquist
    high_cut /= nyquist

    # Define the filter order
    filter_order = 6

    # Design the band pass Butterworth filter
    band_b, band_a = signal.butter(
        filter_order, [low_cut, high_cut], btype='band')

    # apply band pass
    rpi1_chan_1 = signal.lfilter(band_b, band_a, rpi1_chan_1)
    rpi1_chan_2 = signal.lfilter(band_b, band_a, rpi1_chan_2)
    rpi2_chan_1 = signal.lfilter(band_b, band_a, rpi2_chan_1)
    rpi2_chan_2 = signal.lfilter(band_b, band_a, rpi2_chan_2)

    # remove pop
    siglen = len(rpi1_chan_1)
    front_cut = 1500
    end_cut = 0
    rpi1_chan_1 = rpi1_chan_1[front_cut:siglen-end_cut]
    rpi1_chan_2 = rpi1_chan_2[front_cut:siglen-end_cut]
    rpi2_chan_1 = rpi2_chan_1[front_cut:siglen-end_cut]
    rpi2_chan_2 = rpi2_chan_2[front_cut:siglen-end_cut]

    return rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2


def test_filter(rpi1_wav, rpi2_wav):

    results = loc.signalAquisitionTest(rpi1_wav, rpi2_wav)

    # initialise matplotlib plot that will be displayed
    fig, axes = plt.subplots(2, 2)
    plt.suptitle("Original Signals", fontsize=16)

    # for i in range(0,4):
    #     results["original"][i] = results["original"][i][100000:500000]
    #     results["processed"][i] = results["processed"][i][100000:500000]

    # can add additional plotting here
    axes[0][0].plot(results["original"][2], color="b")
    axes[0][1].plot(results["original"][1], color="g")
    axes[1][0].plot(results["original"][2], color="r")
    axes[1][1].plot(results["original"][3], color="m")

    plt.savefig('Main/results/original_signals.jpg', format='jpg')
    plt.close()

    # initialise matplotlib plot that will be displayed
    fig, axes = plt.subplots(2, 2)
    plt.suptitle("Filtered Signals", fontsize=16)

    # can add additional plotting here
    axes[0][0].plot(results["processed"][2], color="b")
    axes[0][1].plot(results["processed"][1], color="g")
    axes[1][0].plot(results["processed"][2], color="r")
    axes[1][1].plot(results["processed"][3], color="m")

    plt.savefig('Main/results/filtered_signals.jpg', format='jpg')
    plt.close()


def write_to_file(contents,file_name):
    # Open the file for writing
    with open(file_name, "w") as file:
        # Loop through the array and write each element to the file
        for item in contents:
            file.write(str(item) + "\n")

def main():
    rpi1_wav = "Main/bytes/rpi1_next_byte.wav"
    rpi2_wav = "Main/bytes/rpi2_next_byte.wav"

    test_corr("Main/bytes/test.wav","processed", "Filtered Recordings","Main/results/filtered_in_out.jpg")
    test_corr("Main/bytes/test.wav","original", "Original Recordings","Main/results/original_in_out.jpg")
    
    test_filter(rpi1_wav, rpi2_wav)

    print(test_size())

if __name__ == "__main__":
    main()
    
