import subprocess

def getCPUtemp():
    data = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
    return data[:2]+"."+data[3]
