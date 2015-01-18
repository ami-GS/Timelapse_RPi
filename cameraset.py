import time
import cv2
import numpy as np
from threading import Thread, Event
import platform
from imageprocess import ImageProcess
import io
import settings as SET
try:
    from picamera import PiCamera # here cause warning
    import light
except:
    PiCamera = object
    light = None

class Camera(object):
    def __init__(self, DIRNAME, LEDnum, FPS = 25):
        self.num = 1
        self.DIRNAME = DIRNAME
        self.FPS = FPS
        if light:
            self.leds = light.LEDs(LEDnum)
        self.ledState = False
        self.camera = None
        self.t = None
        self.sleep = 0
        self.event = Event()
        self.pro = ImageProcess()
        self.config = self._configPass
        self.latestImg = None
        self.MODE = "normal"
        self.camType = ""
        self.effectType = {"USB":['normal', 'edge', 'motion', 'gray'],
                           "RPi":['normal', 'sketch', 'posterise', 'gpen', 'colorbalance', 'film',
                           'pastel', 'emboss', 'denoise', 'negative', 'hatch', 'colorswap',
                           'colorpoint', 'saturation', 'blur', 'watercolor', 'cartoon',
                           'solarize', 'oilpaint']}

    def init(self):
        if light:
            self.leds.init()

    def setMode(self, mode):
        self.sleep = 0.5
        self.MODE = mode
        print(self.MODE)

    def getMode(self):
        return self.MODE

    def takeImage(self):
        pass

    def timeStamp(self):
        stamp = str(self.num).zfill(SET.ZFILL)
        self.num += 1
        return stamp

    def _configPass(self):
        pass

    def _configWait(self):
        self.event.wait(0.5)
        self.config = self._configPass

    def terminate(self):
        del self.camera

    def getFrame(self):
        pass

    def toggleLED(self):
        if light:
            if self.ledState:
                self.leds.off()
                self.ledState = False
            else:
                self.leds.on()
                self.ledState = True

    def setThread(self, target, args):
        del self.t
        self.t = Thread(target=target, args=args)
        self.t.setDaemon(True)

    def getEffects(self):
        return self.effectType[self.camType]

class usbCamera(Camera):
    def __init__(self, DIRNAME, LEDnum = [3, 5, 7]):
        super(usbCamera, self).__init__(DIRNAME, LEDnum)
        self.framerate = self.FPS
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, SET.WIDTH)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, SET.HEIGHT)
        self.camType = "USB"

    def setMode(self, mode):
        super(usbCamera, self).setMode(mode)
        if self.MODE == 'normal':
            self.pro.getImage = self.pro.normal
        elif self.MODE == 'edge':
            self.pro.getImage = self.pro.edgeDetect
        elif self.MODE == 'gray':
            self.pro.getImage = self.pro.grayImage
        elif self.MODE == 'motion':
            self.pro.getImage = self.pro.motionDetect
        self.sleep = 0

    def takeImage(self):
        _, img = self.camera.read()
        if _:
            cv2.imwrite("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()), img)

    def _getFrame(self):
        _, img = self.camera.read()
        if _:
            #img = self.pro.assign(img, self.MODE) # assign each processing
            img = self.pro.getImage(img)
            return img
        else:
            return -1

    def getFrame(self):
        encimg = cv2.imencode(".jpg", self.latestImg)[1]
        return np.array(encimg).tostring()

    def takePic(self):
        self.latestImg = self._getFrame()

    def getVideoFrame(self):
        return self.latestImg

class piCamera(Camera, PiCamera):
    def __init__(self, DIRNAME, LEDnum = [3, 5, 7],camLED=False):
        super(piCamera, self).__init__(DIRNAME, LEDnum)
        super(Camera, self).__init__()
        self.framerate = self.FPS
        self.resolution = (SET.WIDTH, SET.HEIGHT)
        self.led = camLED
        self.camType = "RPi"
        self.stream = io.BytesIO()
        self.stream2 = io.BytesIO()
        time.sleep(2) #initialize

    def takeImage(self):
        data = np.fromstring(self.latestImg, dtype=np.uint8)
        image = cv2.imdecode(data, 1)
        cv2.imwrite("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()), image)

    def takePic(self):
        #self.leds.on()
        self.stream.seek(0)
        img = self.stream.read()
        #self.leds.off()
        self.latestImg = img

    def getFrame(self):
        return self.latestImg

    def setMode(self, mode):
        super(piCamera, self).setMode(mode)
        if mode == "normal":
            mode = "none"
        self.image_effect = mode
        self.config = self._configWait
        self.sleep = 0

    def getVideoFrame(self):
        self.capture(self.stream2, format="jpeg") #this have error
        self.stream2.seek(0)
        data = np.fromstring(self.stream2.getvalue(), dtype=np.uint8)
        self.stream2.seek(0)
        self.stream2.truncate()
        img = cv2.imdecode(data, 1)
        img = img[:, :, ::-1]
        return img
