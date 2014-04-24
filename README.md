Timelapse_RPi
=============

Time lapse camera for Raspberry Pi

(Another OS is also available)


# Usage
`
python timelapse.py [FPS] [Video length]
`

FPS should be set 0 < FPS <= 10

Video length is 'second'


# warning
Because ffmpeg encoding speed in Raspberry Pi is seriously slow, you had better to use ffmpeg in another workstation.