#! /usr/bin/python3
# -*- coding: UTF-8 -*-
import time
import logging
import threading
from enum import Enum
from auto_eyes import Eyes
from auto_jaw import Jaw
from pir import PIR

logging.basicConfig(level=logging.DEBUG)
class skullState(Enum):
    asleep = 0
    awake  = 1


class Skull():

    def __init__(self):
        self.pir   = PIR()
        self.eyes  = Eyes()
        self.jaw   = Jaw()
        self.state = skullState.asleep
        self.stop  = False
        self.t     = threading.Thread(target=self.run, args=())
        self.t.start()


    def run(self):
        while not self.stop:
            if self.state == skullState.asleep:
                if self.pir.motion_detected():
                    self.wakeUp()

            else:  # awake
                #time.sleep(15)   # let it run for at least 15 seconds
                self.gotoSleep()
            time.sleep(0.3)

    def wakeUp(self):
        self.eyes.setAuto(True)
        #self.jaw.doRandomAudio()
        self.jaw.doNextAudio()
        self.state = skullState.awake


    def gotoSleep(self):
        self.eyes.setAuto(False)
        self.jaw.setAuto(False)
        time.sleep(2)
        self.eyes.closed()
        self.jaw.closed()
        self.state = skullState.asleep

    def exit(self):
        self.stop = True
        self.jaw.exit()
        self.eyes.exit()
        self.t.join


if __name__ == "__main__":
    try:
        skull = Skull()
        while True:
            # the skull runs automatically
            time.sleep(60)
        logging.info("quit:")
    except IOError as e:
        print("Exception during init")
        logging.info(e)    
    except KeyboardInterrupt:
        logging.info("quit:")
        skull.exit()
    exit()
