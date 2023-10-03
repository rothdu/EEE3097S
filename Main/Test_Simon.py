from scipy.io import wavfile
import numpy as np
import scipy.optimize
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt
import time
import matplotlib.pyplot as plt
import gcc_phat
from scipy import signal

SR, rpi1 = wavfile.read(
    "/home/simon/EEE3097_Repo_2/EEE3097S/Main/bytes/rpi1_next_byte.wav")
# SR, sig2 = wavfile.read("Main/rpi2_next_byte.wav")
SR, rpi2 = wavfile.read(
    "/home/simon/EEE3097_Repo_2/EEE3097S/Main/bytes/rpi2_next_byte.wav")
# sig1 = sig[:,0]
rpi1_chan_1 = rpi1[:, 0]
rpi1_chan_2 = rpi1[:, 1]
rpi2_chan_1 = rpi2[:, 0]
rpi2_chan_2 = rpi2[:, 1]


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

# Design the low-pass Butterworth filter
high_b, high_a = signal.butter(filter_order, cutoff_frequency, btype='high')

# Design the band pass Butterworth filter
band_b, band_a = signal.butter(filter_order, [low_cut, high_cut], btype='band')


# plot before filtering and cutting
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 8))
ax1.plot(rpi1_chan_1)
ax1.set_title("rpi1_chan_1")
ax2.plot(rpi1_chan_2)
ax2.set_title("rpi1_chan_2")
ax3.plot(rpi2_chan_1)
ax3.set_title("rpi2_chan_1")
ax4.plot(rpi2_chan_2)
ax4.set_title("rpi2_chan_2")
plt.subplots_adjust(hspace=0.5)
plt.suptitle('plot before filtering and cutting ')
plt.show()

# apply high pass
# rpi1_chan_1 = signal.lfilter(high_b, high_a, rpi1_chan_1)
# rpi1_chan_2 = signal.lfilter(high_b, high_a, rpi1_chan_2)
# rpi2_chan_1 = signal.lfilter(high_b, high_a, rpi2_chan_1)
# rpi2_chan_2 = signal.lfilter(high_b, high_a, rpi2_chan_2)

# apply band pass
rpi1_chan_1 = signal.lfilter(band_b, band_a, rpi1_chan_1)
rpi1_chan_2 = signal.lfilter(band_b, band_a, rpi1_chan_2)
rpi2_chan_1 = signal.lfilter(band_b, band_a, rpi2_chan_1)
rpi2_chan_2 = signal.lfilter(band_b, band_a, rpi2_chan_2)

siglen = len(rpi1_chan_1)
front_cut = 1000
end_cut = 0
rpi1_chan_1 = rpi1_chan_1[front_cut:siglen-end_cut]
rpi1_chan_2 = rpi1_chan_2[front_cut:siglen-end_cut]
rpi2_chan_1 = rpi2_chan_1[front_cut:siglen-end_cut]
rpi2_chan_2 = rpi2_chan_2[front_cut:siglen-end_cut]

# plot after filtering and cutting
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 8))
ax1.plot(rpi1_chan_1)
ax1.set_title("rpi1_chan_1")
ax2.plot(rpi1_chan_2)
ax2.set_title("rpi1_chan_2")
ax3.plot(rpi2_chan_1)
ax3.set_title("rpi2_chan_1")
ax4.plot(rpi2_chan_2)
ax4.set_title("rpi2_chan_2")
plt.subplots_adjust(hspace=0.5)
plt.suptitle('plot after filtering and cutting ')
plt.show()

max_tau = 0.01

# tdoa_own = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi2_chan_1, SR, max_tau)  # bottom right mic
# tdoa_other_1 = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi1_chan_1, SR, max_tau)  # top right mic
# tdoa_other_2 = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi1_chan_2, SR, max_tau)  # top left mic

# tdoa rpi1
tdoa_rpi1 = gcc_phat.gcc_phat(
    rpi1_chan_1, rpi1_chan_2, SR, max_tau)  # top left mic

# tdoa rpi2
tdoa_rpi2 = gcc_phat.gcc_phat(
    rpi2_chan_1, rpi2_chan_2, SR, max_tau)  # top left mic

x, y = meshgrid(arange(0, 0.8, 0.01), arange(0, 0.5, 0.01))

# h_other = sqrt((x)**2+(y)**2) - sqrt((x-0.8)**2+(y-0)**2) - \
#     (tdoa_own*constant.speed_of_sound)

# h_other_1 = sqrt((x)**2+(y)**2) - sqrt((x-0.8)**2+(y-0.5)**2) - \
#     (tdoa_other_1*constant.speed_of_sound)

# h_other_2 = sqrt((x)**2+(y)**2) - sqrt((x-0.0)**2+(y-0.5)**2) - \
#     (tdoa_other_2*constant.speed_of_sound)

# testing rpi 1
h_rpi1_test = sqrt((x)**2+(y)**2) - sqrt((x-0.8)**2+(y-0)**2) - \
    (tdoa_rpi1*constant.speed_of_sound)

# testing rpi 2
h_rpi2_test = sqrt((x)**2+(y)**2) - sqrt((x-0)**2+(y-0.5)**2) - \
    (tdoa_rpi2*constant.speed_of_sound)

# print("tdoa_own = " + str(tdoa_own))
# print("tdoa_other_1 = " + str(tdoa_other_1))
# print("tdoa_other_2 = " + str(tdoa_other_2))
print("tdoa_rpi1= " + str(tdoa_rpi1))
print("tdoa_rpi2= " + str(tdoa_rpi2))

# plt.contour(x, y, h_other, [0])
# plt.contour(x, y, h_other_1, [0])
# plt.contour(x, y, h_other_2, [0])
plt.contour(x, y, h_rpi1_test, [0])
plt.contour(x, y, h_rpi2_test, [0])

plt.show()
