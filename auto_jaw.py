import random
import time
from enum import Enum
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import threading

class JawState(Enum):
    closed = 0
    opened = 1

jawDwell   = 4

class Jaw():
    def __init__(self, gpio=19):
        self.servo = Servo(gpio, pin_factory=PiGPIOFactory())
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
                print(self.state)


