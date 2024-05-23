import subprocess
import threading
import os
import sys
from time import sleep
import schedule
from init_db import init_db
from lock_file import create_lock, is_locked, remove_lock

try:
    init_db()
except Exception as err:
    print(f"init_db::Error: {err}", file=sys.stderr)

SCRIPT_PATH = os.getcwd() + "/scrapper_main.py"

print("SCRIPT_PATH ==>> ", SCRIPT_PATH)


def job():
    if is_locked():
        print("Job is already running. Exiting this instance.")
        return

    try:
        create_lock()
        subprocess.run(["python3", SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")
    finally:
        remove_lock()


def threaded_job():
    threading.Thread(target=job).start()


print("!!!!!!!!Scheduling job!!!!!!")
# schedule.every().minute.do(job)
schedule.every().day.at("04:00", "UTC").do(threaded_job)
print("!!!!!!!!Scheduled!!!!!!")


while True:
    schedule.run_pending()
    sleep(0.1)
