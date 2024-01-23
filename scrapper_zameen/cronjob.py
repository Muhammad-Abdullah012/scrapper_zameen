import subprocess
import schedule
import time

script_path = './scrape.py'


def job():
    try:
        subprocess.run(['python3', script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


schedule.every().day.at("05:30", "UTC").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
