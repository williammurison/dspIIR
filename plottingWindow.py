import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

'''credit to bernd porr'''

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self, onThreshold, automationThreshold):

        # create a plot window
        self.fig, self.ax = plt.subplots()

        # that's our plotbuffer
        self.plotbuffer = np.zeros(500)

        # plot the thresholds as lines
        self.onThresholdArray = np.ones(500) * onThreshold
        self.automationThresholdArray = np.ones(500) * automationThreshold

        self.onThresholdLine = self.ax.plot(self.onThresholdArray, label='On Threshold')
        self.automationThresholdLine = self.ax.plot(self.automationThresholdArray, label='Automation Threshold')

        # create an empty line and legend
        self.line, = self.ax.plot(self.plotbuffer, label='Sampling Rate: 0 Hz')
        self.legend = plt.legend()

        # axis
        self.ax.set_ylim(0, 1.5)

        # That's our ringbuffer which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []

        # add any initialisation code here (filters etc)
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)

        # use these to calculate and display the current actual sampling rate
        self.start = 0
        self.end = 1

    # updates the plot
    def update(self, data):

        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)

        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []

        # set the new 500 points of channel 9
        self.line.set_ydata(self.plotbuffer)

        return self.line,

    # appends data to the ringbuffer
    def addData(self, v):

        # track from the length of time to get back to this function
        self.end = time.time()

        # calculate the actual sampling rate
        try:
            actualSamplingRate = 1 / (self.end - self.start) # in Hz
        except ZeroDivisionError:
            actualSamplingRate = 0

        # update the legend to display the sampling rate
        self.legend.get_texts()[0].set_text(f'Sampling rate: {round(actualSamplingRate, 2)} Hz')

        self.start = time.time()

        self.ringbuffer.append(v)