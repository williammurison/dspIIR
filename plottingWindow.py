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
            actualSamplingRate = None
        
        self.start = time.time()

        # update the legend to display the sampling rate
        if not actualSamplingRate == None:
            self.legend.get_texts()[2].set_text(f'Sampling rate: {str(actualSamplingRate)[:6]} Hz') #dont want it to be longer than 6 digits

        self.ringbuffer.append(v)

        # color the background accordingly
        if v > self.automationThresholdArray[0]:
            
            automationRange = 1 - self.automationThresholdArray[0]

            # map v from automation range to 0 - 1 (0 - 0.3 to 0 - 1)
            colorBlend = (v - self.automationThresholdArray[0]) / automationRange

            # find a color between these two based on the value of v
            col1 = [0.70,1.00,0.40] # green
            col2 = [0.0,1.0,0.0] # dark green

            r = (col1[0] * (1 - colorBlend) + col2[0] * colorBlend)
            g = (col1[1] * (1 - colorBlend) + col2[1] * colorBlend)
            b = (col1[2] * (1 - colorBlend) + col2[2] * colorBlend)

            self.fig.patch.set_facecolor((r,g,b))
            self.ax.patch.set_facecolor((r,g,b))

        elif v > self.onThresholdArray[0]:

            self.fig.patch.set_facecolor((0.70,1.00,0.40)) # green in rgb
            self.ax.patch.set_facecolor((0.70,1.00,0.40))

        else:

            self.fig.patch.set_facecolor('snow')
            self.ax.patch.set_facecolor('snow')