class MidiSlider:

    def __init__(self, threshold):

        # the threshold which determines when the switch is "on" (0 to 1)
        self.threshold = threshold

        # store if the switch was on at the last sample
        self.switchOn = False

        # store this here so can compare against other sliders for automation
        self.data = 0

    def updateStatus(self, data):

        # note is off
        if not self.switchOn:
            # check to see if its over the low threshold and if it is turn it on
            if data > self.threshold:
                self.switchOn = True

        # note is on
        else:
            # check to see if note is under low threshold and if it is turn it off
            if data < self.threshold:
                self.switchOn = False
        
        self.data = data

class MidiGlove:

    def __init__(self, midiout, onThreshold, automationThreshold, baseNote):

        self.midiout = midiout

        self.onThreshold = onThreshold
        self.automationThreshold = automationThreshold

        # set up a slider for each of four fingers
        self.index = MidiSlider(onThreshold)
        self.middle = MidiSlider(onThreshold)
        self.ring = MidiSlider(onThreshold)
        self.pinky = MidiSlider(onThreshold)

        # middle C
        self.baseNote = baseNote

        # current note
        self.previousNote = None

    def updateMessages(self):

        # store which sliders are on in a list
        binaryNoteList = [0, 0, 0, 0]

        if self.index.switchOn == True:
            binaryNoteList[0] = 1
        if self.middle.switchOn == True:
            binaryNoteList[1] = 1
        if self.ring.switchOn == True:
            binaryNoteList[2] = 1
        if self.pinky.switchOn == True:
            binaryNoteList[3] = 1

        # convert this to a base ten int
        intNote = 0

        for idx in binaryNoteList:
            intNote = 2 * intNote + idx

        if intNote == 0:
            # when nothing is on no note
            note = None
        else:
            # convert the binary to decimal and then add it to the base note, so octave plus 3 notes
            # minus one since we use 0 for no note
            note = self.baseNote + intNote - 1

        #only send messages if the note has changed
        if not note == self.previousNote:

            # end the previous note if it exists
            if not self.previousNote == None:
                self.midiout.send_message([0x80, self.previousNote, 50])

            # if theres a new note, send it
            if not note == None:
                self.midiout.send_message([0x90, note, 112])
            
            # store the current note for next time
            self.previousNote = note

            print(note)

    def tryAutomation(self):

        largestData = 0

        # find the largest sample of all the sliders
        if self.index.data > largestData:
            largestData = self.index.data
        
        if self.middle.data > largestData:
            largestData = self.middle.data
        
        if self.ring.data > largestData:
            largestData = self.ring.data
        
        if self.pinky.data > largestData:
            largestData = self.pinky.data

        if largestData > self.automationThreshold:

            automationRange = 1 - self.automationThreshold

            # convert from range of data to range of midi (0 - 0.3 to 0 - 126)
            mod = int((largestData - self.automationThreshold) / automationRange * 126)

            # send the message, controlling modulatoin in this case
            mod_msg = [0xB0, 1, mod]
            self.midiout.send_message(mod_msg)
