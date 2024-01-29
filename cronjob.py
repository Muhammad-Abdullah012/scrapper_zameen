import subprocess
import os
import sys
from time import sleep
import schedule
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
# schedule.every().minute.do(job)
schedule.every().day.at("11:00", "UTC").do(job)
print("!!!!!!!!Scheduled!!!!!!")


while True:
    schedule.run_pending()
    sleep(0.1)
