#!/usr/bin/python3

from gpiozero import Servo
import time
import sys
from auto_eyes import Eye
from auto_jaw import Jaw
from pir import PIR

#sensor = PIR()
#while not sensor.detected:
#    time.sleep(.1)
#print("detected")
#while sensor.detected:
#    time.sleep(.1)
#print("not detected")
#sensor.exit()
#exit()

jaw=Jaw()
jaw.setAuto(False)

sequence = [ 1, -.7, 0.3, -0.3, 0.3, -0.3, 0.3]

for value in sequence:
    jaw.setValue(value)
    time.sleep(.25)
jaw.closed()
jaw.exit()

#lid = Eyelid()

#try:
#    time.sleep(10)
#    lid.setAuto(False)
#    time.sleep(5)
#    lid.closed()
#    time.sleep(10)
#    lid.open()
#    time.sleep(10)
#    lid.exit()
#except KeyboardInterrupt:
#    lid.exit()
#    sys.exit(0)

#iris = Iris()
#try:
#    time.sleep(60)
#    iris.exit()
#
#except KeyboardInterrupt:
#    iris.exit()
#    sys.exit(0)

#eye = Eye()
#jaw = Jaw()
#
#try:
#    time.sleep(60)
#    eye.exit()
#    jaw.exit()
#
#except KeyboardInterrupt:
#    eye.exit()
#    jaw.exit()
#    sys.exit(0)
#

