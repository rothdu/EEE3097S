from scipy.io import wavfile
import numpy as np
import scipy.optimize
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt
import time
import matplotlib.pyplot as plt
import gcc_phat

SR, rpi1 = wavfile.read("Main/rpi1_next_byte.wav")
# SR, sig2 = wavfile.read("Main/rpi2_next_byte.wav")
SR, rpi2 = wavfile.read("Main/rpi2_next_byte.wav")
# sig1 = sig[:,0]
rpi1_chan_1 = rpi1[:, 0]
rpi1_chan_2 = rpi1[:, 1]
rpi2_chan_1 = rpi2[:, 0]
rpi2_chan_2 = rpi2[:, 1]
# min_value = sig1.min()

# sig1 = (sig1 - min_value) / (max_value-min_value)
# min_value = sig2.min()

# sig2 = (sig2 - min_value) / (max_value-min_value)

# sig1 = sig1*3
# sig2 = sig2*3

# fft1 = np.fft.rfft(sig1)
# fft2 = np.fft.rfft(sig2)

# l = len(fft1)
# f1 = 100
# f2 = 5000
# bandpass = np.append(np.zeros(f1),np.ones(f2-f1))
# bandpass = np.append(bandpass,np.zeros(l-f2))
# fft1 = np.multiply(fft1,bandpass)
# fft2 = np.multiply(fft2,bandpass)

# sig1 = np.fft.irfft(fft1)
# sig2 = np.fft.irfft(fft2)

siglen = len(rpi1_chan_1)
front_cut = 50000
end_cut = 0
rpi1_chan_1 = rpi1_chan_1[front_cut:siglen-end_cut]
rpi1_chan_2 = rpi1_chan_2[front_cut:siglen-end_cut]
rpi2_chan_1 = rpi2_chan_1[front_cut:siglen-end_cut]
rpi2_chan_2 = rpi2_chan_2[front_cut:siglen-end_cut]

# max_value1 = sig1.max()
# max_value2 = sig2.max()
# sig2 = sig2*(max_value1/max_value2)

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(rpi2_chan_2)
# plt.show()
# plt.plot(rpi2_chan_1)
# plt.show()
# plt.plot(rpi2_chan_2)  # refsig

ax2.plot(rpi2_chan_1)
plt.show()

# tdoa_own = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi2_chan_1, SR, 0.0027)  # bottom right mic
# tdoa_other_1 = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi1_chan_1, SR, 0.0027)  # top right mic
# tdoa_other_2 = gcc_phat.gcc_phat(
#     rpi2_chan_2, rpi1_chan_2, SR, 0.0027)  # top left mic

# tdoa rpi1
tdoa_rpi1 = gcc_phat.gcc_phat(
    rpi1_chan_1, rpi1_chan_2, SR, 0.0027)  # top left mic

# tdoa rpi1
tdoa_rpi2 = gcc_phat.gcc_phat(
    rpi2_chan_2, rpi2_chan_1, SR, 0.0027)  # top left mic

x, y = meshgrid(arange(0, 1, 0.1), arange(0, 0.7, 0.1))

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
print("tdoa_other_1 = " + str(tdoa_rpi1))
print("tdoa_other_2 = " + str(tdoa_rpi2))

# plt.contour(x, y, h_other, [0])
# plt.contour(x, y, h_other_1, [0])
# plt.contour(x, y, h_other_2, [0])
plt.contour(x, y, h_rpi1_test, [0])
plt.contour(x, y, h_rpi2_test, [0])

plt.show()
