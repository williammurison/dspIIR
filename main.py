#!/usr/bin/python3

from pyfirmata2 import Arduino

import rtmidi

import numpy as np
import matplotlib.pyplot as plt

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

#synth connection
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

threshold = 0.5

C_on = [0x90, 60, 112]
C_off = [0x80, 60, 50]

E_on = [0x90, 64, 112]
E_off = [0x80, 64, 50]

G_on = [0x90, 67, 112]
G_off = [0x80, 67, 50]

c_on = [0x90, 72, 112]
c_off = [0x80, 72, 50]

cc_message = [0xB0, 1, 0]
midiout.send_message(cc_message)

index_down = False
middle_down = False
ring_down = False
pinky_down = False

#Automation
automationThreshold = 0.7

# called for every new sample which has arrived from the Arduino
def callBack0(data):

    # add any filtering here:
    # data = self.myfilter.dofilter(data)

    global index_down

    # note is off
    if not index_down:
        # check to see if its over the threshold and if it is turn it on
        if data > threshold:
            midiout.send_message(C_on)
            index_down = True

    # note is on
    else:
        # check to see if note is under threshold and if it is turn it off
        if data < threshold:
            midiout.send_message(C_off)
            index_down = False

        if data > automationThreshold:

            automationRange = 1 - automationThreshold
            #convert from range of data to range of midi (0 - 0.3 to 0 - 126)
            mod = int((data - automationThreshold) / automationRange * 126)

            mod_msg = [0xB0, 1, mod]
            midiout.send_message(mod_msg)

    realtimePlotWindow0.addData(data)

def callBack1(data):
    
    global middle_down

    # note is off
    if not middle_down:
        # check to see if its over the threshold and if it is turn it on
        if data > threshold:
            midiout.send_message(E_on)
            middle_down = True

    # note is on
    else:
        # check to see if note is under threshold and if it is turn it off
        if data < threshold:
            midiout.send_message(E_off)
            middle_down = False

    realtimePlotWindow1.addData(data)

def callBack2(data):
    
    global ring_down

    # note is off
    if not ring_down:
        # check to see if its over the threshold and if it is turn it on
        if data > threshold:
            midiout.send_message(G_on)
            ring_down = True

    # note is on
    else:
        # check to see if note is under threshold and if it is turn it off
        if data < threshold:
            midiout.send_message(G_off)
            ring_down = False

    realtimePlotWindow2.addData(data)

def callBack3(data):
    
    global pinky_down

    # note is off
    if not pinky_down:
        # check to see if its over the threshold and if it is turn it on
        if data > threshold:
            midiout.send_message(c_on)
            pinky_down = True

    # note is on
    else:
        # check to see if note is under threshold and if it is turn it off
        if data < threshold:
            midiout.send_message(c_off)
            pinky_down = False

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

plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")