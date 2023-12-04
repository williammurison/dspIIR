import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

'''Based on code written by Bernd Porr'''

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self, onThreshold, automationThreshold, figureName):

        # create a plot window
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(figureName)

        # that's our plotbuffers
        self.plotbufferClean = np.zeros(500)
        self.plotbufferNoisy = np.zeros(500)

        # plot the thresholds as lines
        self.onThresholdArray = np.ones(500) * onThreshold
        self.automationThresholdArray = np.ones(500) * automationThreshold

        self.onThresholdLine = self.ax.plot(self.onThresholdArray, label='On Threshold')
        self.automationThresholdLine = self.ax.plot(self.automationThresholdArray, label='Automation Threshold')

        # create empty lines and legend
        self.lineNoisy, = self.ax.plot(self.plotbufferNoisy, label='Noisy Signal')
        self.lineClean, = self.ax.plot(self.plotbufferClean, label='CleanSignal\nSampling Rate: 0 Hz')
        self.legend = plt.legend()

        
        # connect close event to saving plot
        self.figName = figureName
        self.fig.canvas.mpl_connect('close_event', self.saveFig)

        # axis
        self.ax.set_ylim(0, 1.5)

        # That's our ringbuffers which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbufferClean = []
        self.ringbufferNoisy = []

        # add any initialisation code here (filters etc)
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)

        # use these to calculate and display the current actual sampling rate
        self.start = 0
        self.end = 1

    # updates the plot
    def update(self, data):

        # add new data to the buffers
        self.plotbufferClean = np.append(self.plotbufferClean, self.ringbufferClean)
        self.plotbufferNoisy = np.append(self.plotbufferNoisy, self.ringbufferNoisy)

        # only keep the 500 newest ones and discard the old ones
        self.plotbufferClean = self.plotbufferClean[-500:]
        self.ringbufferClean = []
        self.plotbufferNoisy = self.plotbufferNoisy[-500:]
        self.ringbufferNoisy = []

        # set the new 500 points of channel 9
        self.lineClean.set_ydata(self.plotbufferClean)
        self.lineNoisy.set_ydata(self.plotbufferNoisy)

        return [self.lineClean, self.lineNoisy],

    # appends data to the ringbuffer
    def addData(self, clean, noisy):

        # track from the length of time to get back to this function
        self.end = time.time()

        # calculate the actual sampling rate
        try:
            actualSamplingRate = 1 / (self.end - self.start) # in Hz
        except ZeroDivisionError:
            actualSamplingRate = None
        
        self.start = self.end

        # update the legend to display the sampling rate
        if not actualSamplingRate == None:
            self.legend.get_texts()[3].set_text(f'CleanSignal\nSampling Rate: {str(actualSamplingRate)[:6]} Hz') #dont want it to be longer than 6 digits

        self.ringbufferClean.append(clean)
        self.ringbufferNoisy.append(noisy)

        # color the background accordingly
        if clean > self.automationThresholdArray[0]:
            
            automationRange = 1 - self.automationThresholdArray[0]

            # map v from automation range to 0 - 1 (0 - 0.3 to 0 - 1)
            colorBlend = (clean - self.automationThresholdArray[0]) / automationRange

            # find a color between these two based on the value of v
            col1 = [0.70,1.00,0.40] # green
            col2 = [0.0,1.0,0.0] # dark green

            r = (col1[0] * (1 - colorBlend) + col2[0] * colorBlend)
            g = (col1[1] * (1 - colorBlend) + col2[1] * colorBlend)
            b = (col1[2] * (1 - colorBlend) + col2[2] * colorBlend)

            self.fig.patch.set_facecolor((r,g,b))
            self.ax.patch.set_facecolor((r,g,b))

        elif clean > self.onThresholdArray[0]:

            self.fig.patch.set_facecolor((0.70,1.00,0.40)) # green in rgb
            self.ax.patch.set_facecolor((0.70,1.00,0.40))

        else:

            self.fig.patch.set_facecolor('snow')
            self.ax.patch.set_facecolor('snow')

    def saveFig(self, event):

        # saving figs
        import os
        def getRelPath(name):
            return str(os.path.join(os.path.dirname(__file__), os.path.abspath(name)))

        self.fig.savefig(getRelPath(f"figs/{self.figName}.svg"), format='svg', dpi=1200)