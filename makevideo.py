import os
import platform
import subprocess
import cv2
import settings as SET

FOURCC = cv2.cv.CV_FOURCC("m","p","4","v")

class MakeVideo():
    def __init__(self, DIRNAME, FPS):
        self.DIRNAME = DIRNAME
        self.FPS = FPS

    def ffmpeg(self):
        if platform.system() == "Darwin":
            subprocess.call(["ffmpeg", "-r", "%f" % SET.ENCODEFPS,
                             "-i", "%%0%dd.jpg" % SET.ZFILL,
                             "-vcodec", "libx264", "-q", "0", "-vf",
                             "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                             "%s/%s-%dfps.mp4" % (self.DIRNAME, self.DIRNAME, self.FPS)]) # for another platform
        else:
            subprocess.call(["ffmpeg", "-r", "%f" % SET.ENCODEFPS,
                             "-i", "%s/%%0%dd.jpg" % (self.DIRNAME, SET.ZFILL),
                             "-r", "%f" % SET.ENCODEFPS, "-an",
                             "-vcodec", "libx264", "-pix_fmt", "yuv420p",
                             "%s/%s-%dfps.mp4" % (self.DIRNAME, self.DIRNAME, self.FPS)]) # for RPi

    def initWriter(self, size):
        self.writer = cv2.VideoWriter()
        success = self.writer.open(self.DIRNAME+"/%s-%dfps.mp4" % (self.DIRNAME, self.FPS),
                                   FOURCC, SET.ENCODEFPS, size, True)

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        self.writer.release()
