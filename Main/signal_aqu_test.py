from scipy.io import wavfile
import numpy as np
import next_byte
import os
from scipy import signal
import matplotlib.pyplot as plt
import localize as loc


def get_signal():
    rpi1_fin_path = "Main/rpi1_finnished.txt"
    rpi2_fin_path = "Main/rpi2_finnished.txt"
    rpi1_wav = "Main/bytes/rpi1_next_byte.wav"
    rpi2_wav = "Main/bytes/rpi2_next_byte.wav"

    next_byte.inform_ready("192.168.137.99", "rpi1")
    found = False
    while not found:
        found = next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)
    
    SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = readSignal(
        rpi1_wav, rpi2_wav)
    
    return rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2
    
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


def test_corr(test_file):
    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = get_signal()
    actual = actual_to_array(test_file)
    recorded = [rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2]

    results = []
    for rec in recorded:
        rec = rec[:len(actual)]
        corr = similarity(actual,rec)
        results.append(corr)
    
    ave = sum(results)/len(results)
    results.append("###")
    results.append(ave)

    return results

def test_size():
    rpi1_wav = "Main/bytes/rpi1_next_byte.wav"
    rpi2_wav = "Main/bytes/rpi2_next_byte.wav"
    
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


def test_filter(rpi1_ip,rpi1_fin_path, rpi2_fin_path,rpi1_wav, rpi2_wav):

    # next_byte.inform_ready(rpi1_ip, "rpi1")
    # next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)

    results = loc.signalAquisitionTest(rpi1_wav, rpi2_wav)

    # initialise matplotlib plot that will be displayed
    fig, axes = plt.subplots(2, 2)
    plt.suptitle("Original Signals", fontsize=16)

    # can add additional plotting here
    axes[0][0].plot(results["original"][0], color="b")
    axes[0][1].plot(results["original"][1], color="g")
    axes[1][0].plot(results["original"][2], color="r")
    axes[1][1].plot(results["original"][3], color="m")

    plt.savefig('Main/results/original_signals.jpg', format='jpg')
    plt.close()

    # initialise matplotlib plot that will be displayed
    fig, axes = plt.subplots(2, 2)
    plt.suptitle("Filtered Signals", fontsize=16)

    # can add additional plotting here
    axes[0][0].plot(results["processed"][0], color="b")
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
    rpi1_fin_path = "Main/rpi1_finnished.txt"
    rpi2_fin_path = "Main/rpi2_finnished.txt"
    rpi1_wav = "Main/bytes/rpi1_next_byte.wav"
    rpi2_wav = "Main/bytes/rpi2_next_byte.wav"

    # results = test_corr("test.wav")
    # write_to_file(results,"Main/results/signal_aqu_corr.txt")
    
    test_filter("192.168.137.99",rpi1_fin_path, rpi2_fin_path,rpi1_wav, rpi2_wav)

    print(test_size())

if __name__ == "__main__":
    main()
    
