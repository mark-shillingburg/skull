import random
import time
from enum import Enum
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import threading
from pygame import mixer
from dataclasses import dataclass

VOLUME = 0.4

minPulse = 0.00090  # in seconds (eg. 0.750ms)
maxPulse = 0.00122  # in seconds (eg. 1.2500ms
jawDwell = 4

class JawSequence():
    def __init__(self, rpt=1, seq=()):
        self.rpt = rpt
        self.seq = seq

class AudioSequence():
    def __init__(self, audio="", volume=.4, jawSeq=()):
        self.audio = audio
        self.volume = volume
        self.jawSeq = jawSeq

LaughSeq0 = JawSequence(1, ([-1, .8], ))
LaughSeq1 = JawSequence(1, ([ 1, .5], ))
LaughSeq2 = JawSequence(6, ([-.1, .25], [.6, .20]))
LaughSeq3 = JawSequence(7, ([-.1, .25], [.6, .25]))
LaughSeq4 = JawSequence(2, (LaughSeq1, LaughSeq3))
LaughSeq  = JawSequence(1, (LaughSeq0, LaughSeq1, LaughSeq2, LaughSeq4))
LaughAudioSeq =  AudioSequence("VincentPriceLaugh.wav", .5, LaughSeq)

# I alone remain
PainSeq0 = JawSequence(1, ([-1, 1], [.8, .4], [-.5, .1], [.8, .4], [-.2, .6], [.6, .2], [0, .1], [.8, .2], [-.8, 1.2]))
# to bring delivery
PainSeq1 = JawSequence(1, ([.6, .3], [-.5, .2], [.8, .5], [-.5, .4], [.7, .2], [-.5, .1], [.7, .1], [-.5, .1], [.7, .3], [-.5, .3] ))
# of your pain
PainSeq2 = JawSequence(1, ([.6, .2], [-.5, .3], [.8, .3], [-.5, .2], [.8, .4], [-1, 2], ))

PainSeq      = JawSequence(1, (PainSeq0, PainSeq1, PainSeq2))
PainAudioSeq = AudioSequence("DeliveryOfYourPain.MP3", .9, PainSeq)

# Freaks
FreaksSeq0 = JawSequence(1, ([-1, 1.8], [.6, .3], [-.7, 1.7], ))
# all of you
FreaksSeq1 = JawSequence(1, ([.7, .2], [-.5, .2], [.5, .1], [-.5, .1], ))
# all of you freaks 
FreaksSeq2 = JawSequence(1, ([-.8, 1.1], FreaksSeq1, [.6, .3], [-.9, .6], ))
# mutations
FreaksSeq3 = JawSequence(1, ([.5, .2], [-.5, .2], [.7, .3], [-.5, .2], [.3, .2], [-1, 2], ))

FreaksSeq      = JawSequence(1, (FreaksSeq0, FreaksSeq1, FreaksSeq2, FreaksSeq3))
FreaksAudioSeq = AudioSequence("Freaks.wav", .9, FreaksSeq)

#                                      Now,                 twelve               long                 hours
DriveSeq0 = JawSequence(1, ([-1, 1.7], [.6, .4], [-.7, .9], [.7, .3], [-.5, .2], [.5, .2], [-.5, .2], [.7, .3], [-.7, .6], ))
#                           before                         the sun              will rise
DriveSeq1 = JawSequence(1, ([.7, .2], [-.5, .2], [.5, .3], [-.5, .1], [.5, .3], [-.7, 1.3], ))
#                           drive                them                  back 
DriveSeq2 = JawSequence(1, ([.6, .3], [-.6, .2], [.6, .2], [-.5, .2], [.8, .2], [-.7, .2], ))
#                           to                   darkness
DriveSeq3 = JawSequence(1, ([.5, .1], [-.5, .1], [.6, .3], [-1, 2], ))

DriveSeq = (DriveSeq0, DriveSeq1, DriveSeq2, DriveSeq3)
DriveAudioSeq = AudioSequence("DriveThemBackIntoDarkness.wav", .9, DriveSeq)

#                                      Doctor...
DeadSeq0 = JawSequence(1, ([-1, .4], [.7, .4], [0, .1], [-.7, 1.1], ))
#                          I                    am
DeadSeq1 = JawSequence(1, ([.7, .3], [-.5, .2], [.7, .3], [-.5, .2], ))
#                          already                       dead
DeadSeq2 = JawSequence(1, ([.7, .1], [0, .1], [.6, .1], [-.7, 1.2], [.7, .2], [-1, 1], ))
 
DeadSeq = (DeadSeq0, DeadSeq1, DeadSeq2)
DeadAudioSeq = AudioSequence("AlreadyDead.wav", .9, DeadSeq)

#                                   If                   you                  so much 
ExecSeq0 = JawSequence(1, ([-1, 1], [.7, .2], [-.5, .1], [.7, .2], [-.5, .1], [.7, .4], [-.5, .1],  ))
#                          as                    show                your 
ExecSeq1 = JawSequence(1, ([.7, .1], [-.5, .1], [.7, .2], [-.5, .1], [.7, .2], [-.5, .1], ))
#                          masks                around               here                 again
ExecSeq2 = JawSequence(1, ([.7, .2], [-.5, .1], [.7, .3], [-.5, .1], [.7, .2], [-.5, .1], [.7, .3], [-.5, .3], ))
#                          I'll               have                  you                 excuted
ExecSeq3 = JawSequence(1, ([.7, .2], [0, .1], [.7, .2], [-.5, .2], [.7, .1], [-.5, .1], [.7, .4], [-1, 1], ))

ExecSeq = (ExecSeq0, ExecSeq1, ExecSeq2, ExecSeq3)
ExecAudioSeq = AudioSequence("Executed.wav", .9, ExecSeq)

AudioSeqList = [LaughAudioSeq, PainAudioSeq, FreaksAudioSeq, DriveAudioSeq, DeadAudioSeq, ExecAudioSeq]

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
        self.lastPlayed = len(AudioSeqList)-1
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
        mixer.music.set_volume(audioSequence.volume)
        self.doJawSequence(audioSequence.jawSeq)
        self.closed()

    def doRandomAudio(self):
        self.lastPlayed = random.randint(0, len(AudioSeqList)-1)
        self.doAudioSequence(AudioSeqList[self.lastPlayed])

    def doNextAudio(self):
        self.lastPlayed += 1
        if self.lastPlayed == len(AudioSeqList):
            self.lastPlayed = 0
        print(self.lastPlayed)
        self.doAudioSequence(AudioSeqList[self.lastPlayed])

if __name__ == "__main__":
    jaw = Jaw()
    jaw.setAuto(False)
    for x in range(len(AudioSeqList)):
        jaw.doNextAudio()
    #jaw.doAudioSequence(ExecAudioSeq)
    jaw.exit()



