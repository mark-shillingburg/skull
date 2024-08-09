import random
import time
from enum import Enum
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import threading
from pygame import mixer
from dataclasses import dataclass

VOLUME = 0.4

minPulse = 0.00091  # in seconds (eg. 0.750ms)
maxPulse = 0.00122  # in seconds (eg. 1.2500ms
jawDwell = 4

class JawSequence():
    def __init__(self, rpt=1, seq=()):
        self.rpt = rpt
        self.seq = seq

class AudioSequence():
    def __init__(self, audio="", jawSeq=()):
        self.audio = audio
        self.jawSeq = jawSeq

LaughSeq0 = JawSequence(1, ([-1, .8], ))
LaughSeq1 = JawSequence(1, ([ 1, .5], ))
LaughSeq2 = JawSequence(6, ([-.1, .25], [.6, .20]))
LaughSeq3 = JawSequence(7, ([-.1, .25], [.6, .25]))
LaughSeq4 = JawSequence(2, (LaughSeq1, LaughSeq3))
LaughSeq  = JawSequence(1, (LaughSeq0, LaughSeq1, LaughSeq2, LaughSeq4))
LaughAudioSeq =  AudioSequence("VincentPriceLaugh.wav", LaughSeq)

AudioSeqList = (LaughAudioSeq, LaughAudioSeq)

def isJawSequence(sequence):
    return sequence.__class__.__name__ == "JawSequence"

class JawState(Enum):
    closed = 0
    opened = 1

class Jaw():
    def __init__(self, gpio=19):
        self.servo = Servo(gpio, pin_factory=PiGPIOFactory(), min_pulse_width=minPulse, max_pulse_width=maxPulse)
        self.auto = False
        self.stop = False
        self.state = JawState.closed
        self.closed()
        mixer.init()
        mixer.music.set_volume(VOLUME)
        self.t = threading.Thread(target=self.run, args=())
        self.t.start()

    def exit(self):
        self.stop = True
        self.t.join()

    def setAuto(self, auto):
        self.auto = auto

    def opened(self):
        self.servo.max()
        self.state = JawState.opened

    def closed(self):
        self.servo.min()
        self.state = JawState.closed

    def setValue(self, value):
        self.servo.value = value

    def getState(self):
        return self.state

    def run(self):
        while not self.stop:
            if not self.auto:
                time.sleep(1)
            else:
                if (self.getState() == JawState.closed):
                    self.opened()
                else:
                    self.closed()
                time.sleep(random.randint(1,jawDwell))
                #print(self.state)            
    
    def doJawSequence(self, sequence):
        if isJawSequence(sequence):
            for r in range(sequence.rpt):
                self.doJawSequence(sequence.seq)
        else:
            for x in range(len(sequence)):
                entry = sequence[x]
                if isJawSequence(entry):
                    self.doJawSequence(entry)
                else:
                    self.servo.value = entry[0]
                    time.sleep(entry[1])

    def doAudioSequence(self, audioSequence):
        mixer.music.load(audioSequence.audio)
        mixer.music.play()
        self.doJawSequence(audioSequence.jawSeq)
        self.closed()

    def doRandomAudio(self):
        audioSeq = random.choice(AudioSeqList)
        self.doAudioSequence(audioSeq)

if __name__ == "__main__":
    jaw = Jaw()
    jaw.setAuto(False)
    jaw.doRandomAudio()
    jaw.exit()




