from scipy.io import wavfile
import numpy as np
import scipy.optimize
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt
import gcc_phat
from scipy import signal
from scipy.optimize import least_squares


def localize(path1, path2, micPos, startTime, hyperbola=False, refTDOA=False):

    returnDict = {
        "result": [],
        "hyperbola": [],
        "reftdoa": [],
        "times": [startTime],
        "errorMessage": []
    }

    SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = readSignal(
        path1, path2)

    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = processSignal(
        rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2)

    max_tau = 0.01

    # tdoa rpi1
    tdoa_rpi1 = gcc_phat.gcc_phat(
        rpi1_chan_1, rpi1_chan_2, SR, max_tau)  # top left mic

    # tdoa rpi2
    tdoa_rpi2 = gcc_phat.gcc_phat(
        rpi2_chan_1, rpi2_chan_2, SR, max_tau)  # top left mic

    print("tdoa_rpi1= " + str(tdoa_rpi1))
    print("tdoa_rpi2= " + str(tdoa_rpi2))

    Valid = True

    if (tdoa_rpi1 == 0 or tdoa_rpi2 == 0):
        Valid = False
        returnDict["errorMessage"].append("GCC-PHAT returned an invalid TDOA")

    else:
        def function(variables):
            (x, y) = variables
            e1 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2) - \
                (tdoa_rpi1*constant.speed_of_sound)
            e2 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2) - \
                (tdoa_rpi2*constant.speed_of_sound)
            return [e1, e2]
        try:
            ans_arr = scipy.optimize.fsolve(function, (0.4, 0.25))

            if (ans_arr[0] < 0 or ans_arr[0] > 0.8 or ans_arr[1] < 0 or ans_arr[1] > 0.5):
                Valid = False
                returnDict["errorMessage"].append("Triangluation couldn't find an intersection")

        except:
            print("An exception occurred")
            Valid = False

        
            returnDict["errorMessage"].append("Triangluation produced a value outside of the grid")

    if hyperbola and Valid:
        hyperbolas = genHyperbola(micPos, tdoa_rpi1, tdoa_rpi2)
        returnDict["hyperbola"] += hyperbolas

    if refTDOA and Valid:
        tdoa_pisync = gcc_phat.gcc_phat(rpi2_chan_1, rpi1_chan_1, SR, max_tau)
        if (tdoa_pisync != 0):
            returnDict["reftdoa"].append(tdoa_pisync)

    if Valid:
        returnDict["result"].append(ans_arr[0])
        returnDict["result"].append(ans_arr[1])

    return returnDict


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


def signalAquisitionTest(path1, path2):

    returnDict = {
        "original": [],
        "processed": [],
    }

    SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = readSignal(
        path1, path2)

    returnDict["original"] += [rpi1_chan_1,
                               rpi1_chan_2, rpi2_chan_1, rpi2_chan_2]

    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = processSignal(
        rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2)

    returnDict["result"] += [rpi1_chan_1,
                             rpi1_chan_2, rpi2_chan_1, rpi2_chan_2]

    return returnDict


def tdoaTest(x, y, path1, path2, micPos):

    returnDict = {
        "actualTdoa": [],
        "estiTdoa": [],
        "percentError": []
    }

    d1 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2)
    d2 = sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2)
    d3 = sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2)

    actualTdoa_rpi1 = (d1 - d2)/constant.speed_of_sound
    actualTdoa_rpi2 = (d1 - d3)/constant.speed_of_sound

    returnDict["actualTdoa"] += [actualTdoa_rpi1, actualTdoa_rpi2]

    SR, rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = readSignal(
        path1, path2)

    rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2 = processSignal(
        rpi1_chan_1, rpi1_chan_2, rpi2_chan_1, rpi2_chan_2)

    max_tau = 0.01

    # tdoa rpi1
    tdoa_rpi1 = gcc_phat.gcc_phat(
        rpi1_chan_1, rpi1_chan_2, SR, max_tau)  # top left mic

    # tdoa rpi2
    tdoa_rpi2 = gcc_phat.gcc_phat(
        rpi2_chan_1, rpi2_chan_2, SR, max_tau)  # top left mic

    returnDict["estiTdoa"] += [tdoa_rpi1, tdoa_rpi2]

    returnDict["percentError"].append((actualTdoa_rpi1-tdoa_rpi1)/0.0027)
    returnDict["percentError"].append((actualTdoa_rpi2-tdoa_rpi2)/0.0027)

    return returnDict


def triangulationTest(x, y, micPos):

    returnDict = {
        "result": [],
        "hyperbola": [],
        "percentError": []
    }

    d1 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2)
    d2 = sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2)
    d3 = sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2)

    actualTdoa_rpi1 = (d1 - d2)/constant.speed_of_sound
    actualTdoa_rpi2 = (d1 - d3)/constant.speed_of_sound

    hyperbolas = genHyperbola(micPos, actualTdoa_rpi1, actualTdoa_rpi2)
    returnDict["hyperbola"] += hyperbolas

    def function(variables):
        (x, y) = variables
        e1 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2) - \
            (actualTdoa_rpi1*constant.speed_of_sound)
        e2 = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2) - \
            (actualTdoa_rpi2*constant.speed_of_sound)
        return [e1, e2]

    ans_arr = scipy.optimize.fsolve(function, (0.4, 0.25))

    returnDict["result"].append(ans_arr[0])
    returnDict["result"].append(ans_arr[1])

    returnDict["percentError"].append((x-ans_arr[0])/0.8)
    returnDict["percentError"].append((y-ans_arr[1])/0.5)

    return returnDict


def genHyperbola(micPos, tdoa_rpi1, tdoa_rpi2):
    # defines a meshgrid of x and y, to produce meshgrids h_rpi1_test, h_rpi2_test for plotting
    x, y = meshgrid(arange(0, 0.8, 0.8/100), arange(0, 0.5, 0.5/100))
    # testing rpi 1
    h_rpi1_test = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[1][0])**2+(y-micPos[1][1])**2) - \
        (tdoa_rpi1*constant.speed_of_sound)
    # testing rpi 2
    h_rpi2_test = sqrt((x-micPos[0][0])**2+(y-micPos[0][1])**2) - sqrt((x-micPos[2][0])**2+(y-micPos[2][1])**2) - \
        (tdoa_rpi2*constant.speed_of_sound)

    return [x, y, h_rpi1_test, h_rpi2_test]


def main():
    result = localize("Main/bytes/rpi1_next_byte.wav",
                      "Main/bytes/rpi2_next_byte.wav",
                      [[0, 0.5], [0.8, 0.5], [0.0, 0.0]], False, False)
    triangulationTest([[0, 0.5], [0.8, 0.5], [0.0, 0.0]])
    print(result)


if __name__ == "__main__":
    main()
