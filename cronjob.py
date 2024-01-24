import subprocess
import time
import schedule
from init_db import init_db

with open("errors.logs.txt", mode="a", encoding="utf-8") as errorFile:
    try:
        init_db()
    except Exception as e:
        print(f"init_db::Error: {e}", file=errorFile)

SCRIPT_PATH = './scrape.py'


def job():
    try:
        subprocess.run(['python3', SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


print("!!!!!!!!Scheduling job!!!!!!")
schedule.every().day.at("05:30", "UTC").do(job)
print("!!!!!!!!Scheduled!!!!!!")


while True:
    schedule.run_pending()
    time.sleep(1)
