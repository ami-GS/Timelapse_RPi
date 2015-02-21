from datetime import datetime
import os, sys
import time
import cameraset
import math
import makevideo
import tornado.web, tornado.websocket, tornado.httpserver
import tornado.ioloop
from tornado.ioloop import IOLoop, PeriodicCallback
from jinja2 import Environment, FileSystemLoader
import json
import socket
import settings as SET
import sensor

env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
DIRNAME = "TL_%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
FPS = 0
LENGTH = 0
clients = []

class HttpHandler(tornado.web.RequestHandler):
    def initialize(self, camera):
        self.effects = camera.getEffects()
        self.mode = camera.getMode()

    def get(self):
        tpl = env.get_template("static/index.html")
        html = tpl.render({'host':SET.HOST, 'port': SET.PORT, 'effects':self.effects,
                           'checked':self.effects.index(self.mode), "LED": "OFF" if camera.ledState else "ON"})
        self.write(html.encode('utf-8'))
        self.finish()

class downloadHandler(tornado.web.RequestHandler):
    def get(self):
        file_name = (DIRNAME+"/%s-%dfps.mp4" % (DIRNAME, FPS))
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open(file_name, 'r') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, camera):
        self.camera = camera

    def sendInfo(self):
        self.write_message("temperature:%s" % sensor.getCPUtemp())

    def open(self):
        self.periodicSender = PeriodicCallback(self.sendInfo, 1000)
        self.periodicSender.start()
        self.sendInit()
        setCameraLoop(self.camera)
        self.camera.t.start()
        self.camera.init()
        self.callback = None
        sys.stdout.write("%s : connection opened\n" % self.request.remote_ip)

    def sendInit(self):
        #self.write_message("camType:%s:%s" % (self.camera.camType, self.camera.MODE))
        self.write_message("param:%d:%d:" % (self.camera.pro.param1, self.camera.pro.param2))
        global clients
        if len(clients) == 2:
            if clients[1] == self.request.remote_ip:
                clients[0] = self
                self.write_message("recording")
                self.write_message("remaining:%f" % (float(LENGTH-self.camera.num)/FPS)) # TODO send remaining time
            else:
                sys.stdout.write("%s : connection refused" % self.request.remote_ip)
                self.on_close()
                return
        elif len(clients) == 1:
            #when open connection after finish recording
            clients[0].on_close()
            clients.append(self)
        elif len(clients) == 0 :
            clients.append(self)

    def on_message(self, message):
        def run():
            clients.append(self.request.remote_ip)
            self.writer = makevideo.MakeVideo(DIRNAME, FPS)
            if isinstance(self.camera, cameraset.usbCamera):
                self.callback = PeriodicCallback(self.videoWriter, 1000/FPS)
                self.writer.initWriter((SET.WIDTH, SET.HEIGHT))
            elif isinstance(self.camera, cameraset.piCamera):
                self.callback = PeriodicCallback(self.takeConsecutiveImages, 1000/FPS)
            self.callback.start()
            sys.stdout.write("Start recording\n")

        global FPS, LENGTH

        message = json.loads(message)
        if message[0] == "fps":
            FPS = float(message[1])
        elif message[0] == "length":
            LENGTH = float(message[1])
            LENGTH = LENGTH*SET.ENCODEFPS
        elif message[0] == "LED":
            self.camera.toggleLED()
        elif message[0] == "range1":
            self.camera.pro.setParam(int(message[1]), self.camera.pro.param2)
        elif message[0] == "range2":
            self.camera.pro.setParam(self.camera.pro.param1, int(message[1]))
        elif message[0] == "start":
            if DIRNAME not in os.listdir("./"):
                print("create directory.... %s" % DIRNAME)
                os.mkdir("./%s" % DIRNAME)

            print("This will finish in %d second" % int(int(LENGTH)/int(FPS)))
            run()
        else:
            self.camera.setMode(message[0])

    def takeConsecutiveImages(self):
        self.camera.takeImage()
        self.camera.num += 1
        if self.camera.num > LENGTH:
            self.finishRecording()
            sys.stdout.write("make video? (this is not recommended) [Y/n]")
            if raw_input() == "Y":
                self.writer.ffmpeg()

    def videoWriter(self):
        self.camera.num += 1
        self.writer.write(self.camera.getVideoFrame())
        if self.camera.num > LENGTH:
            self.finishRecording()
            #self.camera.terminate()
            #sys.exit(1)

    def finishRecording(self):
        sys.stdout.write("finish recording\n")
        self.callback.stop()
        clients.pop(1) #make state be non-recording
        if self.ws_connection:
            self.write_message("finish")

    def on_close(self):
        #print self.close_reason, self.close_code # TODO try to connect again when RPi stops sending
        #about above, the error occurs in javascript code, and it could not be catch the error.
        print("%s : connection closed" % self.request.remote_ip)
        self.close()
        self.periodicSender.stop()
        global clients
        if len(clients) != 2:
            clients = []
        else:
            print("Recording is continuing!")

def setCameraLoop(camera):
    if isinstance(camera, cameraset.usbCamera):
        camera.setThread(target=loop, args=(camera,))
    elif isinstance(camera, cameraset.piCamera):
        camera.setThread(target=rloop, args=(camera,))

def rloop(camera):
    #TODO susbend loop to make stable when change the mode
    try:
        for foo in camera.capture_continuous(camera.stream, "jpeg", use_video_port=True):
            time.sleep(camera.sleep)
            camera.config()
            camera.takePic()
            if clients and clients[0].ws_connection:
                clients[0].write_message(camera.getFrame(), binary=True)
            camera.stream.seek(0)
            camera.stream.truncate()
            if not clients:
                break
    except Exception as e:
        print("in rloop", e)


def loop(camera):
    try:
        while clients:
            time.sleep(camera.sleep)
            camera.takePic()
            if clients and clients[0].ws_connection:
                clients[0].write_message(camera.getFrame(), binary=True)
            time.sleep(1.0/camera.framerate)
    except Exception as e:
        print("in loop", e)

def progressbar(NUM, LENGTH):
    out = "["
    sharpNum = int(math.floor(float(NUM)/LENGTH) * 60)
    out += "#"*sharpNum + "]"
    sys.stdout.write("\r%s" % out)
    sys.stdout.flush()

def mainLoop(camera, FPS, LENGTH):
    writer = makevideo.MakeVideo(DIRNAME, FPS)
    while True:
        progressbar(camera.num, LENGTH) # this doesn't work well
        camera.takeImage()
        time.sleep(1.0/FPS)
        if camera.num > LENGTH:
            camera.terminate()
            if raw_input("Make video? [y/n]").lower() == "y":
                writer.ffmpeg()
            break

#TODO ws server hostname should be change according to user's RPi.
def changejsfile(fname):
    jsfile = ""
    with open(fname, "rw") as fr:
        for line in fr.readlines():
            if "HOSTNAME" in line:
                import socket
                line = line[:line.index("HOSTNAME")]+socket.gethostbyname(socket.gethostname())+line[line.index("HOSTNAME")+len("HOSTNAME"):]
            jsfile += line
        print(jsfile)
        fr.write(jsfile)

if __name__ == "__main__":
    if cameraset.PiCamera != object:
        camera = cameraset.piCamera(DIRNAME)
    else:
        camera = cameraset.usbCamera(DIRNAME)
    setCameraLoop(camera)

    app = tornado.web.Application([
                (r"/", HttpHandler, dict(camera=camera)),
                (r"/download", downloadHandler),
                (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static/"}),
                (r"/camera", WSHandler, dict(camera=camera)),
                ])
    #global HOST
    #HOST = "localhost"
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(SET.PORT)
    try:
        IOLoop.instance().start()
    except:
        camera.leds.fin()
