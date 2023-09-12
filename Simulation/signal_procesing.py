# Pink Noise:
# Pink noise is a good choice for simulating background noise, as it has a balanced energy distribution across frequencies.
# Pink noise can represent the general ambient noise in the room, including the voices of people and low-frequency electrical equipment hum.

# Impulse or Burst Noise:
# To simulate sudden noise events like a sudden loud conversation or equipment noise, you can add short bursts or impulses of noise to your pink noise.
# Impulse noise can test how well your system handles abrupt changes in the acoustic environment.

# Gaussian Noise:
# Adding some Gaussian noise to the signal can account for random variations in the ambient noise level.
# Gaussian noise can represent subtle fluctuations in the room's noise due to people moving, changing conversations, or variations in electrical equipment noise.

import numpy as np
import matplotlib.pyplot as plt
import colorednoise as cn
from scipy import signal

# Function to filter out pink noise
def filter_pink_noise(input_signal,sample_rate , low_cutoff, high_cutoff):
    b, a = signal.butter(6, [low_cutoff/(sample_rate/2), high_cutoff/(sample_rate/2)], btype='band')
    return signal.filtfilt(b, a, input_signal)

# Function to filter out impulse noise
def filter_impulse_n(sig):
    impulse_indices = np.where(np.abs(sig) > 0.5)
    filtered_signal = sig.copy()
    filtered_signal[impulse_indices] = 0
    return filtered_signal

# Function to filter out Gaussian noise
def filter_gaussian_n(sig):
    std_dev = np.std(sig)
    filtered_signal = sig - np.mean(sig)
    filtered_signal = filtered_signal / std_dev
    return filtered_signal

# Function to generate pink noise
def gen_pink_n(duration, sample_rate):
    # Generate pink noise using the Voss-McCartney algorithm
    num_samples = int(duration * sample_rate)
    pink_noise = np.random.randn(num_samples)
    b, a = signal.butter(1, 1 / (sample_rate / 2), btype='low')
    return cn.powerlaw_psd_gaussian(1, int(0.01*44100))

# Function to generate impulse noise
def gen_impulse_n(duration, sample_rate):
    # Generate impulse noise (random spikes)
    num_samples = int(duration * sample_rate)
    impulse_noise = np.random.rand(num_samples)
    return impulse_noise.astype(float)
# Function to generate Gaussian noise
def gen_gaussian_n(duration, sample_rate):
    num_samples = int(duration * sample_rate)
    gaussian_noise = np.random.normal(0, 1, num_samples)
    return gaussian_noise

def gen_sig(duration, sample_rate):
    # Parameters for the sine wave
    amplitude = 6.0      
    frequency = 1000.0       

    # Generate a time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Create the clean sine wave
    return amplitude * np.sin(2 * np.pi * frequency * t), t

def plot_sig_noise(t,sig,noise,n_name):
    # Plot the clean sine wave and the noisy signal
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, sig, label='Clean Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Clean Signal')

    plt.subplot(2, 1, 2)
    plt.plot(t, noise + sig, label='Noisy Signal', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Signal with ' + n_name + " Noise")


    plt.tight_layout()
    plt.show()

# main funtcion to test gui.py
def main():
    
    y, x = gen_sig(0.01, 44100)

    pink = gen_pink_n(0.01, 44100)
    gaus = gen_gaussian_n(0.01, 44100)
    imp = gen_impulse_n(0.01, 44100)

    plot_sig_noise(x,y,pink,"Pink")    
    plot_sig_noise(x,y,gaus,"Gaussian")    
    plot_sig_noise(x,y,imp,"Impulse")    

# Check if the script is being run as the main program
if __name__ == "__main__":
    main()