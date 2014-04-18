import time
import cv2

class Camera(object):
    def __init__(self, DIRNAME, ZFILL, WIDTH, HEIGHT):
        self.num = 1
        self.DIRNAME = DIRNAME
        self.ZFILL = ZFILL
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def takeImage(self):
        pass

    def terminate(self):
        pass

    def timeStamp(self):
        stamp = str(self.num).zfill(self.ZFILL)
        self.num += 1
        return stamp

class usbCamera(Camera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360):
        super(usbCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        self.camera = cv2.VideoCapture(0)

    def takeImage(self):
        _, img = self.camera.read()
        if _:
            cv2.imwrite("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()), img)

    def terminate(self):
        del self.camera

class piCamera(Camera):
    def __init__(self, DIRNAME, ZFILL=7, WIDTH=480, HEIGHT=360):
        super(piCamera, self).__init__(DIRNAME, ZFILL, WIDTH, HEIGHT)
        import picamera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.WIDTH, self.HEIGHT)
        time.sleep(2)

    def takeImage(self):
        self.camera.capture("./%s/%s.jpg" % (self.DIRNAME, self.timeStamp()))