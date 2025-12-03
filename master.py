#!/usr/bin/env python3
import RPi.GPIO as GPIO
import subprocess
import time
import base64
import sys
from openai import OpenAI

BtnPin = 11
BuzzPin = 12

client = OpenAI(api_key="API_KEY")
MODEL = "gpt-5-nano-2025-08-07"
IMAGE_PATH = "captured_image.jpg"
RESOLUTION = "680x480"

PROMPT = (
            "Reply with EXACTLY ONE short sentence (<= 15 words) "
            "describing the COLOR and PATTERN of the clothing artifact."
        )


def setup():
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location

    #Button SetUp
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)

    #Buzzer SetUp, Should Beep on Start
    GPIO.setup(BuzzPin, GPIO.OUT)
    GPIO.output(BuzzPin, GPIO.LOW)
    
def detect(chn):
	message(GPIO.input(BtnPin))
	pass


def capture_image(path: str):
    # -S 2 skips a couple frames so exposure settles faster
    subprocess.run(["fswebcam", "-r", RESOLUTION, "-S", "2", "--no-banner", path], check=True)

def to_data_url(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"
    
#--------------------------------------------------------------------------------------------

def extract_text(resp):
    text = getattr(resp, "output_text", None)
    if text:
        return text.strip()
    try:
        for item in getattr(resp, "output", []):
            for part in getattr(item, "content", []):
                if getattr(part, "type", None) in ("output_text", "text") and getattr(part, "text", None):
                    return part.text.strip()
    except Exception:
        pass
    try:
        return resp.model_dump_json(indent=2)
    except Exception:
        return str(resp)

def get_response(prompt, data_url):
    resp = client.responses.create(
        model=MODEL,
        reasoning={"effort": "low"},  # minimize hidden reasoning for speed
        max_output_tokens=1024,  # big headroom -> no practical cap
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": data_url}
            ]
        }],
    )
    print(extract_text(resp))

#--------------------------------------------------------------------------------------------------------------------------------------------


def activate_vibration(x):
    GPIO.output(BuzzPin, GPIO.HIGH)
    time.sleep(x)
    GPIO.output(BuzzPin, GPIO.LOW)
    time.sleep(x)

def button_action(x):
    if x == 0:
        capture_image(IMAGE_PATH)
        print('Image capture successful')
        data_url = to_data_url(IMAGE_PATH)
        activate_vibration(0.5)

        get_response(PROMPT, data_url)
        
    # data_url = to_data_url(IMAGE_PATH)
    if x == 1:
        # print("Image not Taken")
        pass


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        while True:
            button_action(GPIO.input(BtnPin))
            pass
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        GPIO.cleanup()
