import time
import cv2
import numpy as np
import threading
from picamera import PiCamera
from imageprocess import imageProcess
import io

class Camera(object):
    def __init__(self, DIRNAME, ZFILL, WIDTH, HEIGHT):
        self.num = 1
        self.DIRNAME = DIRNAME
        self.ZFILL = ZFILL
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.camera = ""
        self.t = ""
        self.pro = imageProcess()

    def takeImage(self):
        pass

    def timeStamp(self):
        stamp = str(self.num).zfill(self.ZFILL)
        self.num += 1
        return stamp

    def terminate(self):
        del self.camera

    def getFrame(self):
        pass

    def setThread(self, target, args):
        del self.t
        self.t = threading.Thread(target=target, args=args)
        self.t.setDaemon(True)

class usbCamera(Camera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360, FPS=25):
        super(usbCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        self.camera = cv2.VideoCapture(0)
        self.framelate = FPS
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, WIDTH)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, HEIGHT)

    def takeImage(self):
        _, img = self.camera.read()
        if _:
            cv2.imwrite("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()), img)

    def _getFrame(self, process):
        _, img = self.camera.read()
        if _:
            img = self.pro.assign(img, process) # assign each processing
            return img
        else:
            return -1

    def getFrame(self, process="normal"):
        img = self._getFrame(process)
        encimg = cv2.imencode(".jpg", img)[1]
        return np.array(encimg).tostring()
#       return np.array(cv2.imencode(".jpg", img)[1]).tostring()

    def getVideoFrame(self, process="normal"):
        img = self._getFrame(process)
        return img

class piCamera(Camera, PiCamera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360, FPS=25, LED=False):
        super(piCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        super(Camera, self).__init__()
        self.resolution = (self.WIDTH, self.HEIGHT)
        self.framelate = FPS
        self.led = LED
        self.stream = io.BytesIO()
        self.stream2 = io.BytesIO()
        time.sleep(2) #initialize

    def takeImage(self):
        self.capture("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()))

    def getVideoFrame(self):
        self.capture(self.stream2, format="jpeg") #this have error
        self.stream2.seek(0)
        data = np.fromstring(self.stream2.getvalue(), dtype=np.uint8)
        self.stream2.seek(0)
        self.stream2.truncate()
        img = cv2.imdecode(data, 1)
        img = img[:, :, ::-1]
        return img
