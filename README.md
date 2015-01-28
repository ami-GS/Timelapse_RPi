Timelapse_RPi
=============

Time lapse camera for Raspberry Pi
(Mac OS X is also available with limited functions)


## Usage
`
python timelapse.py
`

Please access to Raspberry Pi using browser (http://raspberrypi.local:8080) which implements websocket.
Set the fps and video length you want make by using specified forms, then it returns time until the recording will have finished.
Finally, the time lapse video will be created automatically (manually type [Y] if you use RPi's camera module), you can download the video by pressing button.

### Requirements
- software
  * opencv
  * tornado
  * picamera == 1.2
  * numpy
  * jinja2
- hardware (if possible)
  * Raspberry Pi
  * USB camera or camera module

### Image
![alt tag](https://raw.github.com/ami-GS/Timelapse_RPi/master/image/P1000764.JPG)
