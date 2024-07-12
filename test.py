from gpiozero import Servo
import time
import sys
from auto_eyes import Eye
from auto_jaw import Jaw
from pir import PIR

sensor = PIR()
while not sensor.detected:
    time.sleep(.1)
print("detected")
while sensor.detected:
    time.sleep(.1)
print("not detected")
sensor.exit()
exit()

#jaw=Servo(19)
#while True:
#    time.sleep(1)
#    jaw.min()
#    print("Open")
#    time.sleep(1)
#    jaw.max()
#    print("Closed")

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

