import subprocess
import time
import schedule
from ischedule import schedule as iSchedule, run_loop
# import ischedule.ischedule as iSchedule

# from init_db import init_db

# with open("errors.logs.txt", mode="a", encoding="utf-8") as errorFile:
#     try:
#         init_db()
#     except Exception as e:
#         print(f"init_db::Error: {e}", file=errorFile)

SCRIPT_PATH = './scrape.py'


def job():
    try:
        subprocess.run(['python3', SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


print("!!!!!!!!Scheduling job!!!!!!")
schedule.every().day.at("11:00", "UTC").do(job)
print("!!!!!!!!Scheduled!!!!!!")


iSchedule(schedule.run_pending, interval=0.1)
run_loop()
