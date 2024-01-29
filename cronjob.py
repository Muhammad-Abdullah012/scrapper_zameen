import subprocess
import os
import sys
import schedule
from ischedule import schedule as iSchedule, run_loop
# import ischedule.ischedule as iSchedule
from init_db import init_db

try:
    init_db()
except Exception as e:
    print(f"init_db::Error: {e}", file=sys.stderr)

SCRIPT_PATH = os.getcwd() + '/scrape.py'

print("SCRIPT_PATH ==>> ", SCRIPT_PATH)


def job():
    try:
        subprocess.run(['python3', SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


print("!!!!!!!!Scheduling job!!!!!!")
# job()
schedule.every().day.at("08:00", "UTC").do(job)
print("!!!!!!!!Scheduled!!!!!!")


iSchedule(schedule.run_pending, interval=0.1)
run_loop()
