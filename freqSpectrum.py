from pyfirmata2 import Arduino

import numpy as np
import matplotlib.pyplot as plt

import matplotlib.animation as animation

from midiController import MidiSlider

''' read and record one analog in for a specified length in seconds and create the fft of it
    so that the cutoff freq required for the real time filtering can be determined'''

class dataStorage():
    
    def __init__(self, samplingRate, lengthSeconds):

        self.store = []
        self.samplingRate = samplingRate

        # in indices
        self.length = lengthSeconds * samplingRate

        # create a plot window
        self.fig, self.ax = plt.subplots()
        self.ax.set_xscale('log')
        
        # empty plot
        self.freqAxis = np.linspace(0, self.samplingRate / 2, int(self.length/2))
        self.line, = self.ax.plot(self.freqAxis, np.ones(len(self.freqAxis)))

        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100, cache_frame_data=False)

    def addData(self, data):

        if len(self.store) < self.length:
            self.store.append(data)

    def update(self, data):
        if len(self.store) == self.length:
            # plot the fft of the stored data log-log
            fftData = np.abs(np.fft.fft(np.array(self.store)))

            splitFft = fftData[1: int(len(fftData)/2) + 1] # dont need the DC

            dbData = 10*np.log10(splitFft/np.max(splitFft))

            self.line.set_ydata(dbData)
            self.ax.set_ylim(min(dbData) * 1.1, max(dbData) * 1.1)

            # saving figs
            import os
            def getRelPath(name):
                return str(os.path.join(os.path.dirname(__file__), os.path.abspath(name)))

            self.fig.savefig(getRelPath(f"figs/freqPlot.svg"), format='svg', dpi=1200)
            needs to be called to close the serial port

PORT = Arduino.AUTODETECT

# sampling rate: 100Hz
samplingRate = 100

length = 20 # seconds

dataStore = dataStorage(samplingRate, length)

def callBack(data):
    dataStore.addData(data)

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callbacks which adds the data to the animated plots and enables the callbacks
board.analog[0].register_callback(callBack)
board.analog[0].enable_reporting()

plt.show()

board.exit()