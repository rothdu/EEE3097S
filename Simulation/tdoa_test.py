import numpy as np
import matplotlib.pyplot as plt
import pyroomacoustics

def main():
    fs = 1000
    
    time = np.linspace(0, 10, 10000)
    freq = .5
    phase_1 = 0.



    signal_1 = np.sin((2*np.pi*freq*time) + phase_1)

    phase_2 = 0.5*np.pi

    
    

    signal_2 = np.sin((2*np.pi*freq*time) + phase_2)

    #signal_2 = np.roll(signal_1, 500)
    
    tdoa = pyroomacoustics.experimental.localization.tdoa(signal_2, signal_1, fs=1000)

    print(tdoa)


if __name__ == "__main__":
    main()