from scipy.io import wavfile
import numpy as np
import scipy.optimize
import scipy.constants as constant
from numpy import arange, meshgrid, sqrt
import time
import matplotlib.pyplot as plt
import gcc_phat

SR, sig1 = wavfile.read("Main/rpi1_next_byte.wav")
# SR, sig2 = wavfile.read("Main/rpi2_next_byte.wav")
SR, sig = wavfile.read("Main/rpi2_next_byte.wav")
# sig1 = sig[:,0]
sig2 = sig[:,1]
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

siglen = len(sig1)
sig1 = sig1[60000:siglen-60000]
sig2 = sig2[60000:siglen-60000]

# max_value1 = sig1.max()
# max_value2 = sig2.max()
# sig2 = sig2*(max_value1/max_value2)

plt.plot(sig1)
plt.plot(sig2)
plt.show()

tdoa = gcc_phat.gcc_phat(sig1,sig2,SR)

x, y = meshgrid(arange(0, 0.7, 0.1), arange(-0.5, 0.5, 0.1))
h1 = sqrt((x)**2+(y)**2) - sqrt((x-0.6)**2+(y-0)**2)-(tdoa*constant.speed_of_sound)

print(tdoa)

plt.contour(x,y,h1,[0])
plt.show()
