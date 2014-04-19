import cv2
from datetime import datetime
import os, sys
import subprocess
import cameraset

WIDTH = 2592 # max
HEIGHT = 1944 # max
DIRNAME = "TL_%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
ZFILL = 7
ENCODEFPS = 25

def makeVideo(FPS):
    os.chdir(DIRNAME)
    try:
        subprocess.call(["ffmpeg", "-r", "%f" % ENCODEFPS, "-i", "%%0%dd.jpg" % ZFILL,
                         "-vcodec", "libx264", "-sameq", "-vf",
                         "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                         "%s-%dfps.mp4" % (DIRNAME, FPS)]) # for RPi
    except:
        subprocess.call(["ffmpeg", "-r", "%f" % ENCODEFPS, "-i", "%%0%dd.jpg" % ZFILL,
                         "-vcodec", "libx264", "-q", "0", "-vf",
                         "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                         "%s-%dfps.mp4" % (DIRNAME, FPS)]) # for another platform

def mainLoop(camera, FPS, LENGTH):
    while True:
        print camera.num,
        camera.takeImage()
        cv2.waitKey(int(1000/FPS))
        if camera.num > LENGTH:
            camera.terminate()
            if raw_input("Make video? [y/n]").lower() == "y":
                makeVideo(FPS)
            break

def main(FPS, LENGTH):
    try:
        camera = cameraset.piCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    except:
        camera = cameraset.usbCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)

    if DIRNAME not in os.listdir("./"):
        os.mkdir("./%s" % DIRNAME)
    duration = LENGTH/FPS

    print("This will finish in %d second" % duration)
    mainLoop(camera, FPS, LENGTH)

if __name__ == "__main__":
    args = sys.argv
    try:
        FPS = float(args[1])
        TIME = float(args[2])
    except:
        print("Usage: python timelapse.py [FPS] [Video length]"
              "\ne.g: python timelapse.py 0.5 10")
        sys.exit(-1)

    main(FPS, int(TIME*ENCODEFPS))
