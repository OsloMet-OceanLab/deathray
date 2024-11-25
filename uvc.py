"""
author: @rambech
"""

import gpiod as GPIO
from time import sleep
from numpy import around
from datetime import datetime
from scripts import configuration
from apscheduler.schedulers.background import BackgroundScheduler


# Setup GPIO pin
UVC_pin = 25
chip = GPIO.Chip('gpiochip4')
uvc_line = chip.get_line(UVC_pin)

# Time
uvc_start = "01:00"
uvc_end = "03:00"

def on():
    try:
        uvc_line.request(consumer="LED", type=GPIO.LINE_REQ_DIR_OUT)
        uvc_line.set_value(1)
    finally:
        uvc_line.release()


def off():
    try:
        uvc_line.request(consumer="LED", type=GPIO.LINE_REQ_DIR_OUT)
        uvc_line.set_value(0)
    finally:
        uvc_line.release()


def test():
    try:
        # print("UVC light on!")
        yield "UVC light on"
        on()
        sleep(5)
    finally:
        off()
        print("UVC light off")


def schedule(scheduler: BackgroundScheduler):
    """
    Enables schedules runtime for the lights
    """
       
    time_format = "%H:%M"
    period = 60
    on_time = 2.5
    off_time = period - on_time

    def run_uvc(duration):
        repeat = around(duration / period, 0)
        t1 = datetime.now()
        print(f"{t1} UVC on")

        while repeat > 0:
            on()
            sleep(on_time)
            off()
            sleep(off_time)
            repeat -= 1

        t2 = datetime.now()
        print(f"{t2} UVC off")

    start_time = uvc_start
    end_time = uvc_end
    start_hour, start_min = start_time.split(":")

    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)
    temp = end - start
    duration = temp.total_seconds()
    
    scheduler.add_job(run_uvc, trigger='cron', hour=start_hour, minute=start_min, args=[duration], id="uvc", replace_existing=True, max_instances=1)