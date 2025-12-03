#!/usr/bin/env python3
import RPi.GPIO as GPIO
import subprocess
import base64
import sys
from openai import OpenAI


BtnPin = 11
IMAGE_PATH = "captured_image.jpg"
RESOLUTION = "640x480"  

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)
	
def capture_image(path: str):
    # -S 2 skips a couple frames so exposure settles faster
    subprocess.run(["fswebcam", "-r", RESOLUTION, "-S", "2", "--no-banner", path], check=True)
    
def to_data_url(path: str) -> str:
	with open(path, "rb") as f:
		b64 = base64.b64encode(f.read()).decode("utf-8")
	return f"data:image/jpeg;base64,{b64}"
	


def message(x):
	if x == 0:
		capture_image(IMAGE_PATH)
		print('Image capture successful')
        #data_url = to_data_url(IMAGE_PATH)
	if x == 1:
		#print("Image not Taken")
		pass

def detect(chn):
	message(GPIO.input(BtnPin))
	pass
	



def destroy():
	# GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	# GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		#loop()
		while True:
			message(GPIO.input(BtnPin))
			pass
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
