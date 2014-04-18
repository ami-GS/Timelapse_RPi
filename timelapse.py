import cv2
from datetime import datetime
import os, sys
import subprocess
import cameraset

WIDTH = 860 # 2592 max
HEIGHT = 720 # 1944 max
DIRNAME = "TL_%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
ZFILL = 7

def makeVideo(FPS):
    os.chdir(DIRNAME)
    print FPS
    subprocess.call(["ffmpeg", "-r", "%f" % FPS, "-i", "%%0%dd.jpg" % ZFILL,
                     "-vcodec", "libx264", "-q", "0", "-vf",
                     "scale=1620:1080,pad=1920:1080:150:0,setdar=16:9",
                     "%s-%dfps.mp4" % (DIRNAME, FPS)])
def mainLoop(camera, FPS, LENGTH):
    while True:
        print camera.num
        camera.takeImage()
        cv2.waitKey(int(1000/FPS))
        if camera.num == LENGTH+1:
            camera.terminate()
            makeVideo(FPS)
            break

def main(FPS, LENGTH):
    try:
        camera = cameraset.piCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    except:
        camera = cameraset.usbCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)

    if DIRNAME not in os.listdir("./"):
        os.mkdir("./%s" % DIRNAME)
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

    main(FPS, int(TIME/FPS))
