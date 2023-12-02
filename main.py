#!/usr/bin/python3

from pyfirmata2 import Arduino
import iir_filter

import rtmidi

import scipy.signal as signal
import matplotlib.pyplot as plt

from plottingWindow import RealtimePlotWindow
from midiController import MidiGlove

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

onThreshold = 0.5
automationThreshold = 0.7

# Create a plotting window for each analog in
plot0 = RealtimePlotWindow(onThreshold, automationThreshold)
plot1 = RealtimePlotWindow(onThreshold, automationThreshold)
plot2 = RealtimePlotWindow(onThreshold, automationThreshold)
plot3 = RealtimePlotWindow(onThreshold, automationThreshold)

# resolution of monitors for putting the plots in nice places
resolutionX = 1920
resolutionY = 1080

# in pixels, want quadrants for half width and height
figWidth = int(resolutionX / 2)
figHeight = int(resolutionY / 2)

pad = 50

# one plot per quadrant of the screen
plot0.fig.canvas.manager.window.setGeometry(int(pad/2), int(pad/2), figWidth - pad, figHeight - pad)
plot1.fig.canvas.manager.window.setGeometry(figWidth + int(pad/2), int(pad/2), figWidth - pad, figHeight - pad)
plot2.fig.canvas.manager.window.setGeometry(int(pad/2), figHeight + int(pad/2), figWidth - pad, figHeight - pad)
plot3.fig.canvas.manager.window.setGeometry(figWidth + int(pad/2), figHeight + int(pad/2), figWidth - pad, figHeight - pad)

# sampling rate: 1000Hz
samplingRate = 100

# synth connection
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

#print(available_ports)

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

baseNote = 60 # middle C
scale = 'major'

# create a controller
controller = MidiGlove(midiout, onThreshold, automationThreshold, baseNote, scale)

# declare the lowpass cutoff frequency in Hz
cutOff = 20

# create filter coefficients and filter object
sos = signal.butter(4, cutOff/samplingRate * 2, 'lowpass', output='sos')
indexFilter = iir_filter.IIR_filter(sos)
middleFilter = iir_filter.IIR_filter(sos)
ringFilter = iir_filter.IIR_filter(sos)
pinkyFilter = iir_filter.IIR_filter(sos)

# called for every new sample which has arrived from the relevant port
def callBack0(data):

    # filter the data
    cleanData = indexFilter.filter(data)

    # turn on or off the note if necessary
    controller.index.updateStatus(cleanData)

    # update the messages and try to do automation
    # only need to call this in one call back as the function checks all the slider values
    controller.updateMessages()
    controller.tryAutomation()

    # update the plot
    plot0.addData(cleanData, data)

def callBack1(data):
    cleanData = middleFilter.filter(data)
    controller.middle.updateStatus(cleanData)
    plot1.addData(cleanData, data)

def callBack2(data):
    cleanData = ringFilter.filter(data)
    controller.ring.updateStatus(cleanData)
    plot2.addData(cleanData, data)

def callBack3(data):
    cleanData = pinkyFilter.filter(data)
    controller.pinky.updateStatus(cleanData)
    plot3.addData(cleanData, data)

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callbacks which adds the data to the animated plots and enables the callbacks
board.analog[0].register_callback(callBack0)
board.analog[0].enable_reporting()

board.analog[1].register_callback(callBack1)
board.analog[1].enable_reporting()

board.analog[2].register_callback(callBack2)
board.analog[2].enable_reporting()

board.analog[3].register_callback(callBack3)
board.analog[3].enable_reporting()

#format and show the plots
plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")