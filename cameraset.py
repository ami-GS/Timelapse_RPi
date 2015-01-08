import time
import cv2
import numpy as np
from threading import Thread, Event
from imageprocess import imageProcess
import io
import settings as SET
try:
    from picamera import PiCamera # here cause warning
except:
    PiCamera = object

class Camera(object):
    def __init__(self, DIRNAME, FPS = 25):
        self.num = 1
        self.DIRNAME = DIRNAME
        self.FPS = FPS
        self.camera = None
        self.t = None
        self.sleep = 0
        self.event = Event()
        self.pro = imageProcess()
        self.config = self._configPass
        self.MODE = "normal"
        self.camType = ""
        self.effectType = {"USB":['normal', 'edge', 'motion', 'gray'],
                           "RPi":['normal', 'sketch', 'posterise', 'gpen', 'colorbalance', 'film',
                           'pastel', 'emboss', 'denoise', 'negative', 'hatch', 'colorswap',
                           'colorpoint', 'saturation', 'blur', 'watercolor', 'cartoon',
                           'solarize', 'oilpaint']}

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

    def setThread(self, target, args):
        del self.t
        self.t = Thread(target=target, args=args)
        self.t.setDaemon(True)

    def getEffects(self):
        return self.effectType[self.camType]

class usbCamera(Camera):
    def __init__(self, DIRNAME):
        super(usbCamera, self).__init__(DIRNAME)
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
        img = self._getFrame()
        encimg = cv2.imencode(".jpg", img)[1]
        return np.array(encimg).tostring()
#       return np.array(cv2.imencode(".jpg", img)[1]).tostring()

    def getVideoFrame(self):
        img = self._getFrame()
        return img

class piCamera(Camera, PiCamera):
    def __init__(self, DIRNAME, LED=False):
        super(piCamera, self).__init__(DIRNAME)
        super(Camera, self).__init__()
        self.framerate = self.FPS
        self.resolution = (SET.WIDTH, SET.HEIGHT)
        self.led = LED
        self.camType = "RPi"
        self.stream = io.BytesIO()
        self.stream2 = io.BytesIO()
        time.sleep(2) #initialize

    def takeImage(self):
        self.capture("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()))

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
