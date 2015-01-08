import RPi.GPIO as GPIO

class LEDs():
    def __init__(self, chan_list = []):
        GPIO.setmode(GPIO.BOARD)
        if chan_list:
            self.setChannels(chan_list)

    def setChannels(self, chan_list):
        self.chan_list = chan_list
        GPIO.setup(chan_list, GPIO.OUT)

    def on(self):
        GPIO.output(self.chan_list, GPIO.HIGH)

    def off(self):
        GPIO.output(self.chan_list, GPIO.LOW)

    def fin(self):
        GPIO.cleanup(self.chan_list)
