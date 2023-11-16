import time

import numpy as np
import pyaudio
import matplotlib.pyplot as plt

p = pyaudio.PyAudio()

volume = 0.5  # range [0.0, 1.0]
fs = 44100  # sampling rate, Hz, must be integer
f = 440.0  # sine frequency, Hz, may be float

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

# generate samples, note conversion to float32 array
#1 period of the sine wav
samples = (volume * (np.sin(2 * np.pi * np.arange(fs / f) * f / fs)).astype(np.float32)).tobytes()

# plt.plot(samples)
# plt.show()

duration = 5 * fs

t = 0

print('starting now')

while t < duration:

    if t % len(samples) == 0:

        # play. May repeat with different volume values (if done interactively)
        start_time = time.time()
        stream.write(samples)
        print("Played sound for {:.5f} seconds".format(time.time() - start_time))

    t += 1

stream.stop_stream()
stream.close()

p.terminate()