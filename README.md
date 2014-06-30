Timelapse_RPi
=============

Time lapse camera for Raspberry Pi
(Another Platform is also available)


## Usage
`
python timelapse.py
`

Please access to Raspberry Pi using browser (http://raspberrypi.local:8080) which implements websocket.
Set the fps and video length you want make by using specified form, then it returns time until the recording will have finished.
Finally, the time lapse video will be created automatically, so you should download the video by pressing button.

### Requirements
- software
  * opencv
  * tornado
  * picamera
  * numpy
- hardware (if possible)
  * Raspberry Pi
  * USB camera or camera module

### TODO
* Make it possible to record video from RPi camera module
* fix bugs that sometimes stop showing after switch image effect

# warning
You cannot record when you use Raspberry pi camera module (there are bugs yet sorry)
However, USB camera is available.

