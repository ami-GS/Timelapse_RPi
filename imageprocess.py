import cv2


class imageProcess():
    def __init__(self):
        self.prev = ""
        pass

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
        img = cv2.Canny(img, 100, 200)
        return img

    def grayImage(self, img):
        img = cv2.cvtColor(img, cv2.cv.CV_RGB2GRAY)
        img = cv2.cvtColor(img, cv2.cv.CV_GRAY2RGB)
        return img

    def motionDetect(self, img):
        tmp = cv2.absdiff(self.prev, img)
        tmp = cv2.threshold(tmp, 40, 255, cv2.cv.CV_THRESH_BINARY)[1]
        self.prev = img
        return tmp
