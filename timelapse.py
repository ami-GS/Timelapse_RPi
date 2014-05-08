from datetime import datetime
import os, sys
import time
import cameraset
import math
import makevideo
import tornado.web, tornado.websocket, tornado.httpserver
import tornado.ioloop
from tornado.ioloop import IOLoop, PeriodicCallback
import json

WIDTH = 480 #2592 # max
HEIGHT = 360 #1944 # max
DIRNAME = "TL_%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
ZFILL = 7
ENCODEFPS = 25
FPS = 0
LENGTH = 0
VIDEOMODE = "normal"
CLIENT = [] #[websocket connection object, ip address which recording]
RUN = False


class HttpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, camera):
        self.camera = camera

    def open(self):
        global CLIENT

        if len(CLIENT) == 2:
            if CLIENT[1] == self.request.remote_ip:
                CLIENT[0] = self
                self.write_message("recording")
                self.write_message("remaining:") # TODO send remaining time
            else:
                sys.stdout.write("%s : connection refused" % self.request.remote_ip)
                self.on_close(); return
        elif len(CLIENT) == 0:
            CLIENT.append(self)

        self.setCameraThread(self.camera)

        self.camera.t.start()
        self.callback = ""
        sys.stdout.write("%s : connection opened\n" % self.request.remote_ip)

    def on_message(self, message):
        def run():
            CLIENT.append(self.request.remote_ip)
            self.callback = PeriodicCallback(self.videoWriter, 1000/FPS)
            self.writer = makevideo.makeVideo(DIRNAME, ENCODEFPS, FPS, ZFILL)
            self.writer.initWriter((WIDTH, HEIGHT))
            self.callback.start()
            sys.stdout.write("Start recording")

        global FPS, LENGTH

        message = json.loads(message)

        if len(message) == 2:
            if message[0] == "fps":
                FPS = float(message[1])
            elif message[0] == "length":
                LENGTH = float(message[1])
                LENGTH = LENGTH*ENCODEFPS
        elif len(message) == 1:
            global VIDEOMODE
            VIDEOMODE = message[0]

        if FPS and LENGTH:
            if DIRNAME not in os.listdir("./"):
                print("create directory.... %s" % DIRNAME)
                os.mkdir("./%s" % DIRNAME)

            print("This will finish in %d second" % int(int(LENGTH)/int(FPS)))
            run()

    def videoWriter(self):
        img = self.camera.getVideoFrame()
        self.camera.num += 1
        self.writer.write(img)
        if self.camera.num > LENGTH:
            sys.stdout.write("finish recording\n")
            self.callback.stop()
            #self.camera.terminate()
            #sys.exit(1)

    @classmethod
    def setCameraThread(self, camera):
        if isinstance(camera, cameraset.usbCamera):
            camera.setThread(target=WSHandler.loop, args=(camera,))
        elif isinstance(camera, cameraset.piCamera):
            camera.setThread(target=WSHandler.rloop, args=(camera,))

    @staticmethod
    def rloop(camera):
        try:
            for foo in camera.capture_continuous(camera.stream, "jpeg", use_video_port=True):
                camera.stream.seek(0)
                img = camera.stream.read()
                CLIENT[0].write_message(img, binary=True)
                camera.stream.seek(0)
                camera.stream.truncate()
                if not CLIENT:
                    break
        except Exception as e:
            print "in rloop", e

    @staticmethod
    def loop(camera):
        try:
            while CLIENT:
                img = camera.getFrame(VIDEOMODE)
                CLIENT[0].write_message(img, binary=True)
                time.sleep(1.0/camera.framelate)
        except Exception as e:
            print "in loop", e

    def on_close(self):
        global CLIENT
        print("%s : connection closed" % self.request.remote_ip)

        if len(CLIENT) != 2:
            CLIENT = []
        else:
            print("Recording is continuing!")

def progressbar(NUM, LENGTH):
    out = "["
    sharpNum = int(math.floor(float(NUM)/LENGTH) * 60)
    out += "#"*sharpNum + "]"
    sys.stdout.write("\r%s" % out)
    sys.stdout.flush()

def mainLoop(camera, FPS, LENGTH):
    writer = makevideo.makeVideo(DIRNAME, ENCODEFPS, FPS, ZFILL)
    while True:
        progressbar(camera.num, LENGTH) # this doesn't work well
        camera.takeImage()
        time.sleep(1.0/FPS)
        if camera.num > LENGTH:
            camera.terminate()
            if raw_input("Make video? [y/n]").lower() == "y":
                writer.ffmpeg()
            break

if __name__ == "__main__":
    try:
        camera = cameraset.piCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    except:
        camera = cameraset.usbCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    WSHandler.setCameraThread(camera)

    app = tornado.web.Application([
                (r"/", HttpHandler),
                (r"/camera", WSHandler, dict(camera=camera)),
                ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    IOLoop.instance().start()
