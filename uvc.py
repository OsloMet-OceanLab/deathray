#!/usr/bin/env python3

"""
author: @rambech
"""

import gpiod as GPIO
from time import sleep
from numpy import around
from datetime import datetime
from pytz import timezone
import json
from apscheduler.schedulers.background import BackgroundScheduler
import signal
import sys


# Setup GPIO pin
UVC_pin = 25
chip = GPIO.Chip('gpiochip4')
uvc_line = chip.get_line(UVC_pin)

minutes = 15 * 60

# Get time from config
with open("config.json", "r") as file:
    config = json.load(file)

uvc_start = config["start"]
uvc_end = config["end"]

class ServiceKiller:
    kill = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.kill_service)
        signal.signal(signal.SIGTERM, self.kill_service)

    def kill_service(self, signum, frame):
        self.kill = True
        off()
        sys.exit(0)
        print("Kill signal caught")

def print_jobs(scheduler: BackgroundScheduler):
    count = 0
    for job in scheduler.get_jobs():
        print(f"Job{count}: {job.id}")
        count += 1

    if count < 1:
        print("No new jobs scheduled")

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
    except OSError as e:
        print(f"Experienced OSError: {e}")
        print("Trying again...")
        off()
    finally:
        uvc_line.release()


def test():
    try:
        yield "UVC light on"
        on()
        sleep(5)
    finally:
        off()
        print("UVC light off")


def deathray_schedule(scheduler: BackgroundScheduler, service_killer :ServiceKiller):
    """
    Enables schedules runtime for the lights
    """
       
    time_format = "%H:%M"
    period = 60
    on_time = 2.5
    off_time = period - on_time

    def run_uvc(duration, service_killer :ServiceKiller):
        repeat = around(duration / period, 0)

        while repeat > 0 and not service_killer.kill:
            on()
            print("UVC on")
            sleep(on_time)
            off()
            print("UVC off")
            sleep(off_time)
            repeat -= 1


    start_time = uvc_start
    end_time = uvc_end
    start_hour, start_min = start_time.split(":")

    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)
    temp = end - start
    duration = temp.total_seconds()
    
    scheduler.add_job(run_uvc, trigger='cron', hour=start_hour, minute=start_min, args=[duration, service_killer], id="uvc", replace_existing=True, max_instances=1)
    print("New schedule set:")
    print_jobs(scheduler)


def main():
    try:
        cet = timezone("CET")
        scheduler = BackgroundScheduler()
        scheduler.configure(timezone=cet)
        scheduler.start()

        service_killer = ServiceKiller()
        deathray_schedule(scheduler, service_killer)

        while not service_killer.kill:
            sleep(minutes)
            print("Tick! still alive")

    finally:
        print("Terminating...")
        scheduler.remove_all_jobs()
        print("Scheduled jobs cleared")
        scheduler.shutdown(wait=False)
        print("Scheduler terminated")
        off()
        print("Video lights off")
        print("nightlight.service terminated")


if __name__ == "__main__":
    main()