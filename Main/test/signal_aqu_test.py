from scipy.io import wavfile
import numpy as np
import next_byte
import os

def parent_file_fetch(file):
    parent = os.path.join(os.getcwd(), os.pardir)
    return os.path.join(parent, file)

def get_signal():
    rpi1_fin_path = parent_file_fetch("rpi1_finnished.txt")
    rpi2_fin_path = parent_file_fetch("rpi2_finnished.txt")
    rpi1_wav = parent_file_fetch("bytes/rpi1_next_byte.wav")
    rpi2_wav = parent_file_fetch("bytes/rpi2_next_byte.wav")

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


def test_corr():
    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = get_signal()
    actual = actual_to_array("test.wav")
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
    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = get_signal()
    lengths = [len(rpi1_chan_1), len(rpi1_chan_2), len(rpi2_chan_1), len(rpi2_chan_2)]

    if all(length == lengths[0] for length in lengths):
        result = True
    else:
        result = False

    return result

def write_to_file(contents,file_name):
    # Open the file for writing
    with open(file_name, "w") as file:
        # Loop through the array and write each element to the file
        for item in contents:
            file.write(str(item) + "\n")

def main():
    results = test_corr()
    write_to_file(results,"signal_aqu_corr.txt")
    
    
if __name__ == "__main__":
    main()
    
