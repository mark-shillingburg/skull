
import os
import sys
import time
import spidev
import logging
import numpy as np
from gpiozero import *

# This class is for using SPI bus 0 and multiple devices with 
# a common RST and DC gpios for the devices.
class RpiSpi:
    def __init__(self,spi_freq=40000000,rst = 27,dc = 25):
        self.np=np
        self.INPUT = False
        self.OUTPUT = True

        self.SPEED  =spi_freq

        self.RST_PIN= self.gpio_mode(rst,self.OUTPUT)
        self.DC_PIN = self.gpio_mode(dc,self.OUTPUT)
        
        #Initialize SPI
        self.SPI = {}

    def get_name(self, bus, device):
        return "bus{}_dev{}".format(bus,device)

    def gpio_mode(self,Pin,Mode,pull_up = None,active_state = True):
        if Mode:
            return DigitalOutputDevice(Pin,active_high = True,initial_value =False)
        else:
            return DigitalInputDevice(Pin,pull_up=pull_up,active_state=active_state)

    def digital_write(self, Pin, value):
        if value:
            Pin.on()
        else:
            Pin.off()

    def digital_read(self, Pin):
        return Pin.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def gpio_pwm(self,Pin):
        return PWMOutputDevice(Pin,frequency = self.BL_freq)

    def spi_writebyte(self, bus, device, data):
        name = self.get_name(bus, device)
        if self.SPI[name]!=None :
            self.SPI[name].writebytes(data)

    def device_init(self, bus, device ):
        spi = spidev.SpiDev(bus, device)
        if spi!=None :
            spi.max_speed_hz = self.SPEED        
            spi.mode = 0b00   
        name = self.get_name(bus, device)
        self.SPI[name] = spi
        return 0

    def spi_reset(self):
        """ Reset all devices """
        self.digital_write(self.RST_PIN, True)
        time.sleep(0.01)
        self.digital_write(self.RST_PIN, False)
        time.sleep(0.01)
        self.digital_write(self.RST_PIN, True)
        time.sleep(0.01)

    def spi_exit(self):
        logging.debug("spi end")
        for spi in self.SPI:
            if self.SPI[spi]!=None :
                self.SPI[spi].close()
        
        logging.debug("gpio cleanup...")
        self.digital_write(self.RST_PIN, 1)
        self.digital_write(self.DC_PIN, 0)   
        time.sleep(0.001)


'''
if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    implementation = RaspberryPi()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
'''

### END OF FILE ###
