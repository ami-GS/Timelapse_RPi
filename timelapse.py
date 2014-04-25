from datetime import datetime
import os, sys
import time
import cameraset
import math
import makevideo

WIDTH = 2592 # max
HEIGHT = 1944 # max
DIRNAME = "TL_%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
ZFILL = 7
ENCODEFPS = 25

def progress(NUM, LENGTH):
    out = "["
    sharpNum = int(math.floor(float(NUM)/LENGTH) * 60)
    out += "#"*sharpNum + "]"
    sys.stdout.write("\r%s" % out)
    sys.stdout.flush()

def mainLoop(camera, FPS, LENGTH):
    writer = makevideo.makeVideo(DIRNAME, ENCODEFPS, FPS, ZFILL)
    while True:
        progress(camera.num, LENGTH) # this doesn't work well
        camera.takeImage()
        time.sleep(1.0/FPS)
        if camera.num > LENGTH:
            camera.terminate()
            if raw_input("Make video? [y/n]").lower() == "y":
                writer.ffmpeg()
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
