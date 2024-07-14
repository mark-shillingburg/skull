# Eyes, Eye, Iris, and Eyelid classes

import os
import sys 
import time
import logging
import random
from random import randint
from PIL import Image,ImageDraw,ImageFont
from enum import Enum
import threading
import eye_spi
import lcd_240x240

left      = 0
right     = 1

position = ["right", "left"]
rotation  = {"left":180,"right":0}

# SPI parameters/pins
bus       = {"left":0,  "right":1 } 
dev       = {"left":0,  "right":2} 
rst       = {"left":27, "right":1}  
dc        = {"left":22, "right":12} 
spi_freq  = 150000000

eyes_loop_time = 0.001 # 1 mS


class Eyes():
    def __init__(self):
        image = Image.new("RGB", (240,240), "BLACK")
        self.disp = {}
        self.spi = {}
        for eye in position:
            self.disp[eye] = lcd_240x240.LCD()
            # Use unique SPI instances (unique RST and DC)
            self.spi[eye] = eye_spi.RpiSpi(rst=rst[eye], dc=dc[eye], spi_freq=spi_freq)
            self.spi[eye].spi_reset()
            self.disp[eye].Init(self.spi[eye], bus[eye], dev[eye])
            self.disp[eye].clear()
            self.disp[eye].ShowImage(image)
        self.eye = Eye()    # use single instance to update and draw both eyes
        self.auto = False
        self.stop = False
        self.t = threading.Thread(target=self.run, args=())
        self.t.start()

    def run(self):
        while not self.stop:
            #if not self.auto:
            #    time.sleep(1)
            #else:
                if self.eye.update():
                    self.draw()
                time.sleep(eyes_loop_time)

    def setAuto(self, auto):
        self.auto = auto;
        self.eye.setAuto(auto)
    
    def closed(self):
        self.eye.closed()

    def opened(self):
        self.eye.opened()

    def draw(self):
        image = self.eye.draw()
        for eye in position:
            image = image.rotate(rotation[eye])
            self.disp[eye].ShowImageOffset(image, 60)

    def exit(self):
        self.stop = True
        self.eye.exit()
        for eye in position:
            self.spi[eye].spi_exit()
        self.t.join()


class Eye():
    def __init__(self):
        eyeball = Image.open('pic/eye_ball.bmp')	
        self.eyeball = eyeball.convert("RGB")
        self.lid  = Eyelid()
        self.iris = Iris()
        
    def update(self):
        return  self.iris.update or self.lid.update

    def setAuto(self, auto):
        self.iris.setAuto(auto)
        self.lid.setAuto(auto)

    def closed(self):
        self.lid.closed()

    def opened(self):
        self.lid.opened()

    def draw(self):
        image = self.eyeball.copy()
        self.iris.draw(image)
        self.lid.draw(image)
        return image.crop((0,60,240,180))

    def exit(self):
        self.iris.exit()
        self.lid.exit()


class Direction(Enum):
    static= 0
    up    = 1
    down  = 2
    right = 3
    left  = 4


max_dir   = 6
xstep     = 8
ystep     = 4
max_iris_dwell = 3   # seconds
min_iris_dwell = 0.1 # 10 frames per second movement


class Iris():

    def __init__(self):
        # load the image
        iris = Image.open('pic/iris.bmp')	
        # create a mask from the iris image where 0 is transparent
        iris_mask = Image.new("1", iris.size)

        #  convert the iris to RGBA where (0,0,0) is transparent
        for x in range(iris.width):
            for y in range(iris.height):
                if  (0 == iris.getpixel((x,y))):
                    iris_mask.putpixel((x,y),0)
                else: 
                    iris_mask.putpixel((x,y),1)
        self.width,self.height = iris.size
        self.img  = iris.convert("RGB")
        self.mask = iris_mask
        self.x    = 0
        self.y    = 0
        self.dir  = Direction.static
        self.auto = False
        self.stop = False
        self.update = False
        self.t = threading.Thread(target=self.run, args=())
        self.t.start()

    def run(self):
        while not self.stop:
            if not self.auto:
                time.sleep(1)
            else:
                dwell = min_iris_dwell
                x, y = self.position()
                #print(self.dir, self.x, self.y)
                if (self.dir==Direction.up):
                    if y == max_dir:
                        self.dir = Direction.static
                    else:
                        self.y += 1
                elif (self.dir==Direction.down):
                    if y == -max_dir:
                        self.dir = Direction.static
                    else:
                        self.y -= 1
                elif (self.dir==Direction.right):
                    if x == max_dir:
                        self.dir = Direction.static
                    else:
                        self.x += 1
                        if (y > 0):
                            self.y -=1
                        elif (y < 0):
                            self.y +=1
                elif (self.dir==Direction.left):
                    if x == -max_dir:
                        self.dir = Direction.static
                    else:
                        self.x -= 1
                        if (y > 0):
                            self.y -=1
                        elif (y < 0):
                            self.y +=1
                else: # static
                    dwell = random.randint(1, max_iris_dwell)
                    self.getNextDir()            
                if (self.x, self.y) == (0,0) and (self.x,self.y) != (x,y):
                    self.dir = Direction.static
                time.sleep(dwell)
                self.update = True


    def exit(self):
        self.stop = True
        self.t.join()


    def draw(self, image):
        # calculate x,y based on size and position
        xpos = self.width//2+self.x*xstep
        ypos = self.height//2+self.y*ystep
        # paste into image at xpos, ypos
        image.paste(self.img, (xpos,ypos), self.mask)
        # clear the update flag
        self.update = False
        return

    def position(self):
        return (self.x, self.y)

    def setAuto(self, auto):
        self.auto = auto

    def getNextDir(self):
        x, y = self.position()
        if (x == max_dir):
            self.dir = Direction.left
        elif (x == -max_dir):
            self.dir = Direction.right
        elif (y == max_dir):
            self.dir = random.choice([Direction.down, Direction.right, Direction.left])
        elif (y == -max_dir):
            self.dir = random.choice([Direction.up, Direction.right, Direction.left])
        elif ((x,y) == (0,0)):
            self.dir = random.choice(list(Direction))
                
        

class LidState(Enum):
    opened  = 0
    closing = 1
    closed  = 2
    
closing_dwell  = 0.1 # seconds
closed_dwell   = 0.3 # seconds
max_open_dwell = 2   # seconds


class Eyelid():

    def __init__(self):
        # initialize state
        self.state = LidState.closed
        self.auto  = False
        self.stop  = False
        self.update= False

        # load the images and create the masks
        lid_image = Image.open('pic/eyelid.bmp')

        self.closed_img   = Image.new("RGB", (240,120), "BLACK")
        self.open_img     = lid_image.crop((0,0,240, 120))
        self.closing_img  = lid_image.crop((0,120,240, 240))

        # create the masks for the open and closing eye lids
        self.open_mask = Image.new("1", self.open_img.size)
        for x in range(self.open_img.width):
            for y in range(self.open_img.height):
                if  (7 == self.open_img.getpixel((x,y))):
                    self.open_mask.putpixel((x,y),0)
                else:
                    self.open_mask.putpixel((x,y),1)
        self.open_img = self.open_img.convert("RGB")

        self.closing_mask= Image.new("1", self.closing_img.size)
        for x in range(self.closing_img.width):
            for y in range(self.closing_img.height):
                if  (7 == self.closing_img.getpixel((x,y))):
                    self.closing_mask.putpixel((x,y),0)
                else:
                    self.closing_mask.putpixel((x,y),1)
        self.closing_img = self.closing_img.convert("RGB")

        # create and start the thread
        self.t = threading.Thread(target=self.run, args=())
        self.t.start()

    def opened(self):
        self.state = LidState.opened
        self.update = True

    def closed(self):
        self.state = LidState.closed
        self.update = True
        #print("Lid should be closed")

    def setAuto(self, auto):
        self.auto = auto

    def exit(self):
        self.stop = True
        self.t.join(0.001)

    def run(self):
        while not self.stop:
            if not self.auto:
                time.sleep(1)
                #print(self.state)
            else:
                if self.state == LidState.opened:
                    time.sleep(randint(1, max_open_dwell))
                    self.state = LidState.closing
                elif self.state == LidState.closing:
                    time.sleep(closing_dwell)
                    self.state = LidState.closed
                else:  #closed
                     time.sleep(closed_dwell)
                     self.state = LidState.opened
                self.update = True
                #print(self.state)
                

    def draw(self, image):
        #paste lid based on state
        if (self.state == LidState.closed):
            image.paste(self.closed_img, (0,60))
        elif (self.state == LidState.closing):
            image.paste(self.closing_img, (0,60), self.closing_mask)
        else:
            image.paste(self.open_img, (0,60), self.open_mask)
        # clear the update flag
        self.update = False

