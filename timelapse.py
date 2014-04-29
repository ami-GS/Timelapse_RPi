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
CLIENT = ""
RUN = False

class HttpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, camera):
        self.camera = camera

    def open(self):
        global CLIENT
        if CLIENT:
            sys.stdout.write("%s : connection refused" % self.request.remote_ip)
            self.on_close();return
        CLIENT = self
        self.camera.t.start()
        self.callback = ""
        sys.stdout.write("%s : connection opened\n" % self.request.remote_ip)

    def on_message(self, message):
        def run():
            global RUN
            self.callback = PeriodicCallback(self.videoWriter, 1000/FPS)
            self.writer = makevideo.makeVideo(DIRNAME, ENCODEFPS, FPS, ZFILL)
            self.writer.initWriter((WIDTH, HEIGHT))
            self.callback.start()
            RUN  = True

        global FPS, LENGTH
        if not RUN:
            message = json.loads(message)
            if message[0] == "fps":
                FPS = float(message[1])
            elif message[0] == "length":
                LENGTH = float(message[1])
                DURATION = LENGTH*ENCODEFPS

            if FPS and LENGTH:
                main(FPS, int(DURATION))
                run()

    def videoWriter(self):
        img = self.camera.getVideoFrame()
        self.camera.num += 1
        self.writer.write(img)
        if self.camera.num > LENGTH:
            sys.stdout.write("finish recording\n")
            self.callback.stop()
            self.camera.terminate()
            sys.exit(1)

    @staticmethod
    def rloop(camera):
        try:
            for foo in camera.capture_continuous(camera.stream, "jpeg", use_video_port=True):
                camera.stream.seek(0)
                img = camera.stream.read()
                CLIENT.write_message(img, binary=True)
                camera.stream.seek(0)
                camera.stream.truncate()
                if not CLIENT:
                    break
        except Exception as e:
            print e

    @staticmethod
    def loop(camera):
        try:
            while CLIENT:
                img = camera.getFrame()
                CLIENT.write_message(img, binary=True)
                time.sleep(1.0/25)
        except Exception as e:
            print e

    def on_close(self):
        global CLIENT
        if CLIENT:
            CLIENT = ""
        print("%s : connection closed" % self.request.remote_ip)

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
    if DIRNAME not in os.listdir("./"):
        os.mkdir("./%s" % DIRNAME)
    duration = LENGTH/FPS

    print("This will finish in %d second" % duration)

if __name__ == "__main__":
    try:
        camera = cameraset.piCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
        camera.setThread(target=WSHandler.rloop, args=(camera,))
    except:
        camera = cameraset.usbCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
        camera.setThread(target=WSHandler.loop, args=(camera,))

    app = tornado.web.Application([
                (r"/", HttpHandler),
                (r"/camera", WSHandler, dict(camera=camera)),
                ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    IOLoop.instance().start()
