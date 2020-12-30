#!/usr/bin/env python3

import os
import sys
import time
import random
import signal
import logging
import subprocess

button_pin = 14 #(GPIO14, pin 8) https://www.raspberrypi.org/documentation/usage/gpio/
clipPath = "/media/FISHDISK/"
currentPlayer = None

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
        "Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by "
        "using 'sudo' to run your script")
    sys.exit(1)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(filename="/tmp/fishtank-service.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def get_random_clip():
    return random.choice([f for f in os.listdir(clipPath) if f.endswith('.mp4')])


def stop_clip():
    global currentPlayer
    if currentPlayer is not None:
        try:
            process_group_id = os.getpgid(currentPlayer.pid)
            os.killpg(process_group_id, signal.SIGTERM)
            logger.info('SIGTERM sent to player pid: %s', process_group_id)
            currentPlayer = None
        except OSError:
            logger.error('Could not find the process to kill')
    else:
        logger.info('No player to stop.')


def play_clip(file):
    try:
        stop_clip()
        logger.info('Playing clip: %s', file)
        return subprocess.Popen(["/usr/bin/omxplayer", "-o", "hdmi", "--vol", "1000", "--orientation", "180", "-r", "--loop",
                                 file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                preexec_fn=os.setsid, universal_newlines=True)
    except Exception as e:
        logger.error('Failed to play clip "%s", error: %s', file, e, exc_info=True)


def button_callback(channel):

    start_time = time.time()

    while GPIO.input(channel) == 1: # Wait for the button release
        pass

    buttonTime = time.time() - start_time # How long was the button pressed?
    # a long distinct press of 1 seconds is needed for us to take notice, this is to filter out static.
    if buttonTime >= 1:
        global currentPlayer
        logger.info('Button pressed, changing fishtank clip.')
        currentPlayer = play_clip(get_random_clip())


logging.info('Starting fishtank daemon.')

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# add rising edge detection on a channel, ignoring further edges for 300ms for switch bounce handling
GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_callback, bouncetime=300)

currentPlayer = play_clip(get_random_clip())

try:
    # loop until program exists
    while True:
        if currentPlayer is not None:
            stdout, stderr = currentPlayer.communicate()
            #for line in iter(stdout.readline, b''):  # b'\n'-separated lines
            logging.info('got line from subprocess: %r', stdout)
        time.sleep(30)
except KeyboardInterrupt:
    try:
        GPIO.cleanup()
        stop_clip()
        sys.exit(130)
    except SystemExit:
        os._exit(1)
