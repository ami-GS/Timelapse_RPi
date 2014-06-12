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
        with open("index.html", "r") as f:
            for line in f.readlines():
                self.write(line)
        #self.finish() # TODO Here should be appeared after finish recording. -> DONE
        #self.render("./index.html")

class downloadHandler(tornado.web.RequestHandler):
    def get(self):
        file_name = ("%s-%dfps.mp4" % (DIRNAME, FPS))
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

    def open(self):
        global CLIENT

        if len(CLIENT) == 2:
            if CLIENT[1] == self.request.remote_ip:
                CLIENT[0] = self
                self.write_message("recording")
                self.write_message("remaining:%f" % (float(LENGTH-self.camera.num)/FPS)) # TODO send remaining time
            else:
                sys.stdout.write("%s : connection refused" % self.request.remote_ip)
                self.on_close()
                return
        elif len(CLIENT) == 0:
            CLIENT.append(self)

        self.setCameraLoop(self.camera)

        self.camera.t.start()
        self.callback = ""
        sys.stdout.write("%s : connection opened\n" % self.request.remote_ip)

    def on_message(self, message):
        def run():
            CLIENT.append(self.request.remote_ip)
            if isinstance(self.camera, cameraset.usbCamera):
                self.callback = PeriodicCallback(self.videoWriter, 1000/FPS)
                self.writer = makevideo.makeVideo(DIRNAME, ENCODEFPS, FPS, ZFILL)
                self.writer.initWriter((WIDTH, HEIGHT))
            elif isinstance(self.camera, cameraset.piCamera):
                self.LENGTH = LENGTH
                self.callback = PeriodicCallback(self.takeConsecutiveImages, 1000/FPS)
            self.callback.start()
            sys.stdout.write("Start recording")

        global FPS, LENGTH

        message = json.loads(message)

        if message[0] == "fps":
            FPS = float(message[1])
        elif message[0] == "length":
            LENGTH = float(message[1])
            LENGTH = LENGTH*ENCODEFPS
        elif message[0] == "param1":
            self.camera.pro.setParam(param1=int(message[1]))
        elif message[0] == "param2":
            self.camera.pro.setParam(param2=int(message[1]))
        elif message[0] == "start":
            if DIRNAME not in os.listdir("./"):
                print("create directory.... %s" % DIRNAME)
                os.mkdir("./%s" % DIRNAME)

            print("This will finish in %d second" % int(int(LENGTH)/int(FPS)))
            run()
        else:
            global VIDEOMODE
            VIDEOMODE = message[0]
            if isinstance(camera, cameraset.piCamera):
                camera.image_effect = VIDEOMODE

    def takeConsecutiveImages(self):
        self.camera.takeImage()
        self.camera.num += 1
        if self.camera.num > LENGTH:
            self.finishRecording()
            sys.stdout.write("make video? (this is not recommended) [Y/n]")
            if raw_input() == "Y":
                self.writer.ffmpeg()

    def videoWriter(self):
        img = self.camera.getVideoFrame(VIDEOMODE)
        self.camera.num += 1
        self.writer.write(img)
        if self.camera.num > LENGTH:
            self.finishRecording()
            #self.camera.terminate()
            #sys.exit(1)

    def finishRecording(self):
        sys.stdout.write("finish recording\n")
        self.callback.stop()
        CLIENT.pop(1) #make state be non-recording
        self.write_message("finish")

    @classmethod
    def setCameraLoop(self, camera):
        if isinstance(camera, cameraset.usbCamera):
            camera.setThread(target=WSHandler.loop, args=(camera,))
        elif isinstance(camera, cameraset.piCamera):
            camera.setThread(target=WSHandler.rloop, args=(camera,))

    @staticmethod
    def rloop(camera):
        #TODO susbend loop to make stable when change the mode
        try:
            for foo in camera.capture_continuous(camera.stream, "jpeg", use_video_port=True):
                camera.stream.seek(0)
                img = camera.stream.read()
                #img = np.fromstring(img, dtype=np.uint8).tostring()
                #img = cv2.imdecode(img,1)#.tostring()
                #img = img[:,:,::-1]
                #img = pro.assign(img,VIDEOMODE)
                #error here
                #result, img = cv2.imencode(".jpg", img, [1,90])
                #img = np.array(img).tostring()
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
                time.sleep(1.0/camera.framerate)
        except Exception as e:
            print "in loop", e

    def on_close(self):
        global CLIENT
        #print self.close_reason, self.close_code # TODO try to connect again when RPi stops sending
        #about above, the error occurs in javascript code, and it could not be catch the error.
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

#TODO ws server hostname should be change according to user's RPi.
def changejsfile(fname):
    jsfile = ""
    with open(fname, "rw") as fr:
        for line in fr.readlines():
            if "HOSTNAME" in line:
                import socket
                line = line[:line.index("HOSTNAME")]+socket.gethostbyname(socket.gethostname())+line[line.index("HOSTNAME")+len("HOSTNAME"):]
            jsfile += line
        print jsfile
        fr.write(jsfile)

if __name__ == "__main__":
    try:
        camera = cameraset.piCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    except:
        camera = cameraset.usbCamera(DIRNAME, ZFILL, WIDTH, HEIGHT)
    WSHandler.setCameraLoop(camera)

    app = tornado.web.Application([
                (r"/", HttpHandler),
                (r"/download", downloadHandler),
                (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "./js/"}),
                (r"/camera", WSHandler, dict(camera=camera)),
                ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    IOLoop.instance().start()
