#! /usr/bin/python3
# -*- coding: UTF-8 -*-
import time
import logging
from auto_eyes import Eyes
from auto_jaw import Jaw
from pir import PIR


logging.basicConfig(level=logging.DEBUG)
pir  = PIR()
eyes = Eyes()
jaw  = Jaw()

try:
    while True: 
        pir.waitForMotion()
        eyes.setAuto(True)
        jaw.setAuto(True)
        time.sleep(10)
        pir.waitForNoMotion
        eyes.setAuto(False)
        jaw.setAuto(False)
        time.sleep(2)
        eyes.closed()
        jaw.closed()


    logging.info("quit:")
except IOError as e:
    print("Exception during init")
    logging.info(e)    
except KeyboardInterrupt:
    logging.info("quit:")
    eyes.exit()
    jaw.exit()
exit()
