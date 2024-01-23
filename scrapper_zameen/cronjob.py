import subprocess
import time
import schedule

SCRIPT_PATH = './scrape.py'


def job():
    try:
        subprocess.run(['python3', SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


schedule.every().day.at("05:30", "UTC").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
