from gpiozero import MotionSensor

class PIR():
    def __init__(self, gpio=4, queue=5, threshold=0.5):
        self.sensor = MotionSensor(pin=gpio, queue_len=queue, threshold=threshold)

    def waitForMotion(self):
        return self.sensor.wait_for_motion()

    def waitForNoMotion(self):
        return self.sensor.wait_for_no_motion()

    def motion_detected(self):
        return self.sensor.motion_detected
