import gcc_phat
import next_byte
import os
from scipy.io import wavfile
import gcc_phat
from scipy import signal

def tdoa(path1, path2,):
    SR, rpi1_chan_1, rpi2_chan_1 = readSignal(
        path1, path2)

    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = processSignal(
        rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2)

    max_tau = 0.01

    # tdoa rpi1
    tdoa = gcc_phat.gcc_phat(
        rpi1_chan_1, rpi2_chan_2, SR, max_tau)  # top left mic

    return tdoa

def readSignal(path1, path2):

    # Import Wav files
    SR, rpi1 = wavfile.read(path1)
    SR, rpi2 = wavfile.read(path2)

    # Separate into channels
    rpi1_chan_1 = rpi1[:, 0]
    rpi2_chan_1 = rpi2[:, 0]

    return SR, rpi1_chan_1, rpi2_chan_1


def processSignal(rpi1_chan_1, rpi2_chan_1):

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
    rpi2_chan_1 = signal.lfilter(band_b, band_a, rpi2_chan_1)

    # remove pop
    siglen = len(rpi1_chan_1)
    front_cut = 1500
    end_cut = 0
    rpi1_chan_1 = rpi1_chan_1[front_cut:siglen-end_cut]
    rpi2_chan_1 = rpi2_chan_1[front_cut:siglen-end_cut]

    return rpi1_chan_1, rpi2_chan_1

def write_to_file(contents,file_name):
    # Open the file for writing
    with open(file_name, "w") as file:
        # Loop through the array and write each element to the file
        for item in contents:
            file.write(str(item) + "\n")

def test(max,rpi1_fin_path, rpi2_fin_path, rpi1_wav,rpi2_wav):
    results = []

    for i in range(0,max):
        next_byte.inform_ready("192.168.137.99", "rpi1")
        found = False
        while not found:
            found = next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)
        tdoa = tdoa(rpi1_wav,rpi2_wav)
        results.append(tdoa)

    ave = sum(results)/len(results)
    results.append("###")
    results.append(ave)
    return results

def main():
    rpi1_fin_path = "Main/rpi1_finnished.txt"
    rpi2_fin_path = "Main/rpi2_finnished.txt"
    rpi1_wav = "Main/bytes/rpi1_next_byte.wav"
    rpi2_wav = "Main/bytes/rpi2_next_byte.wav"

    results = test(10,rpi1_fin_path, rpi2_fin_path, rpi1_wav,rpi2_wav)
    write_to_file(results,"Main/results/sync_tdoa_results.txt")
    
    
if __name__ == "__main__":
    main()