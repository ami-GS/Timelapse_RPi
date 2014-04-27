import time
import cv2
import numpy as np
import threading

class Camera(object):
    def __init__(self, DIRNAME, ZFILL, WIDTH, HEIGHT):
        self.num = 1
        self.DIRNAME = DIRNAME
        self.ZFILL = ZFILL
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.camera = ""
        self.t = ""

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
        self.t = threading.Thread(target=target, args=args)
        self.t.setDaemon(True)

class usbCamera(Camera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360):
        super(usbCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, WIDTH)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, HEIGHT)

    def takeImage(self):
        _, img = self.camera.read()
        if _:
            cv2.imwrite("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()), img)

    def _getFrame(self):
        _, img = self.camera.read()
        if _:
            return img
        else:
            return -1

    def getFrame(self):
        img = self._getFrame()
        return np.array(cv2.imencode(".jpg", img)[1]).tostring()

    def getVideoFrame(self):
        img = self._getFrame()
        return img

class piCamera(Camera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360):
        super(piCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        import picamera, io
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.WIDTH, self.HEIGHT)
        self.camera.framerate = 30
        #self.camera.led = False
        self.camera.stream = io.BytesIO()
        time.sleep(2)

    def takeImage(self):
        self.camera.capture("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()))
