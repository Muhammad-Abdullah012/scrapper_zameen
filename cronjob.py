import subprocess
import threading
import os
import sys
from time import sleep
import schedule
from init_db import init_db

try:
    init_db()
except Exception as err:
    print(f"init_db::Error: {err}", file=sys.stderr)

SCRIPT_PATH = os.getcwd() + "/scrape.py"

print("SCRIPT_PATH ==>> ", SCRIPT_PATH)


def job():
    try:
        subprocess.run(["python3", SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


def threaded_job():
    threading.Thread(target=job).start()


print("!!!!!!!!Scheduling job!!!!!!")
# schedule.every().minute.do(job)
schedule.every().day.at("14:00", "UTC").do(threaded_job)
print("!!!!!!!!Scheduled!!!!!!")


while True:
    schedule.run_pending()
    sleep(0.1)
