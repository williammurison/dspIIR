#!/usr/bin/python3

from pyfirmata2 import Arduino

import pyaudio
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from plottingWindow import RealtimePlotWindow

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Create a plotting window for each analog in
realtimePlotWindow0 = RealtimePlotWindow()
realtimePlotWindow1 = RealtimePlotWindow()
realtimePlotWindow2 = RealtimePlotWindow()
realtimePlotWindow3 = RealtimePlotWindow()

# sampling rate: 100Hz
samplingRate = 100

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

# called for every new sample which has arrived from the Arduino
def callBack0(data):

    # add any filtering here:
    # data = self.myfilter.dofilter(data)

    realtimePlotWindow0.addData(data)

def callBack1(data):
    realtimePlotWindow1.addData(data)

def callBack2(data):
    realtimePlotWindow2.addData(data)

def callBack3(data):
    realtimePlotWindow3.addData(data)

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callback which adds the data to the animated plot and enable the callback
board.analog[0].register_callback(callBack0)
board.analog[0].enable_reporting()

board.analog[1].register_callback(callBack1)
board.analog[1].enable_reporting()

board.analog[2].register_callback(callBack2)
board.analog[2].enable_reporting()

board.analog[3].register_callback(callBack3)
board.analog[3].enable_reporting()

t = 0 #track how far along the sine wave we are

plt.show()

# while True:
#     if currentValue1 < 0.5:
#         if t % len(samples) == 0:
#             # play. May repeat with different volume values (if done interactively)
#             start_time = time.time()
#             stream.write(samples)
#             print("Played sound for {:.5f} seconds".format(time.time() - start_time))
#         t += 1

stream.stop_stream()
stream.close()

p.terminate()

# needs to be called to close the serial port
board.exit()

print("finished")