import os
import platform
import subprocess
import cv2

FOURCC = cv2.cv.CV_FOURCC("m","p","4","v")

class makeVideo():
    def __init__(self, DIRNAME, ENCODEFPS, FPS, ZFILL):
        self.DIRNAME = DIRNAME
        self.ENCODEFPS = ENCODEFPS
        self.FPS = FPS
        self.ZFILL = ZFILL

    def ffmpeg(self):
        os.chdir(self.DIRNAME)
        if platform.system() == "Darwin":
            subprocess.call(["ffmpeg", "-r", "%f" % self.ENCODEFPS, "-i", "%%0%dd.jpg" % self.ZFILL,
                             "-vcodec", "libx264", "-q", "0", "-vf",
                             "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                             "%s-%dfps.mp4" % (self.DIRNAME, self.FPS)]) # for another platform
        else:
            subprocess.call(["ffmpeg", "-r", "%f" % self.ENCODEFPS, "-i", "%%0%dd.jpg" % self.ZFILL,
                             "-vcodec", "libx264", "-sameq", "-vf",
                             "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                             "%s-%dfps.mp4" % (self.DIRNAME, self.FPS)]) # for RPi

    def initWriter(self, size):
        os.chdir(self.DIRNAME)
        self.writer = cv2.VideoWriter()
        success = self.writer.open("%s-%dfps.mp4" % (self.DIRNAME, self.FPS),
                                   FOURCC, self.ENCODEFPS, size, True)

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        self.writer.release()