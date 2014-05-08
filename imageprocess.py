import cv2


class imageProcess():
    def __init__(self):
        self.prev = ""
        self.param1 = 100
        self.param2 = 200
        pass

    def setParam(self, param1=100, param2=200):
        self.param1 = param1
        self.param2 = param2

    def assign(self, img, process):
        if process == "normal":
            self.prev = img
            return img

        if process == "edge":
            img = self.edgeDetect(img)
        elif process == "gray":
            img = self.grayImage(img)
        elif process == "motion":
            img = self.motionDetect(img)

        return img

    def edgeDetect(self, img):
        img = cv2.Canny(img, self.param1, self.param2)
        return img

    def grayImage(self, img):
        img = cv2.cvtColor(img, cv2.cv.CV_RGB2GRAY)
        img = cv2.cvtColor(img, cv2.cv.CV_GRAY2RGB)
        return img

    def motionDetect(self, img):
        tmp1 = cv2.cvtColor(self.prev, cv2.cv.CV_RGB2GRAY)
        tmp2 = cv2.cvtColor(img, cv2.cv.CV_RGB2GRAY)
        tmp = cv2.absdiff(tmp1, tmp2)
        tmp = cv2.threshold(tmp, self.param1, self.param2, cv2.cv.CV_THRESH_BINARY)[1]
        self.prev = img
        return tmp
