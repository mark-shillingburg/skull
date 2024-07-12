from gpiozero import MotionSensor

class PIR():
    def __init__(self, gpio=4):
        self.sensor = MotionSensor(gpio)

    def waitForMotion(self):
        return self.sensor.wait_for_motion()

    def waitForNoMotion(self):
        return self.sensor.wait_for_no_motion()
