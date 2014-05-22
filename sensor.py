import mosquitto
import subprocess

#TODO: implement MQTT broker and publisher to transferring sensor data
def Sensor():
    def __init__(self):
        self.client = mosquitto.Mosquitto()

    def getCPUtemp(self):
        data = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
        self.cli.publish("RPi/temp", data, 1)
