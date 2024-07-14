import random
import time
from enum import Enum
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import threading


minPulse = 0.00091  # in seconds (eg. 0.750ms)
maxPulse = 0.00122  # in seconds (eg. 1.2500ms

class JawState(Enum):
    closed = 0
    opened = 1

jawDwell   = 4

class Jaw():
    def __init__(self, gpio=19):
        self.servo = Servo(gpio, pin_factory=PiGPIOFactory(), min_pulse_width=minPulse, max_pulse_width=maxPulse)
        self.auto = False
        self.stop = False
        self.state = JawState.closed
        self.closed()
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
    
    def doSequence(self, sequence):
        for x in range(len(sequence)):
            entry = sequence[x]
            self.servo.value = entry[0]
            time.sleep(entry[1])
        self.closed()

if __name__ == "__main__":
    jaw = Jaw()
    jaw.setAuto(False)
    jaw.doSequence(([1,.5], [0,.25], [1, .5], [0,.25], [1, .5], [0, .25], [1, .5], [0, .5]))
    jaw.exit()


