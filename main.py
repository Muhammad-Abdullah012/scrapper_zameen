from fastapi import FastAPI, BackgroundTasks
import subprocess
import threading
import asyncio
from os import environ, getcwd
from sys import exit
from playwright.async_api import (
    async_playwright,
)
from scrape import search_city, page_loaded, initialize_chromium, is_connected

app = FastAPI()
baseUrl = environ.get("BASE_URL")

if baseUrl is None:
    print("BASE_URL is missing in env file!")
    exit(1)

CRONJOB_SCRIPT_PATH = getcwd() + "/cronjob.py"


def launch_chronjob():
    try:
        subprocess.run(["python3", CRONJOB_SCRIPT_PATH], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")


threading.Thread(target=launch_chronjob).start()


async def scrape_data_by_city(city: str):
    async with async_playwright() as playwright:
        try:
            (page, context, browser, task_queue) = await initialize_chromium(
                playwright=playwright
            )
            await page.goto(baseUrl, timeout=60000)
            await search_city(city=city, page=page)
            await page_loaded(page)

            print("System is connected to internet => ", is_connected())
            tasks = [task_queue.get() for _ in range(task_queue.qsize())]
            print(f"Waiting for {len(tasks)} tasks!!")
            await asyncio.gather(*tasks)
            print("Wait Finished!!")

            await context.close()
            await browser.close()
        except Exception as e:
            return {"message": f"Something went wrong:: {str(e)}"}


async def scrape_data_by_url(url: str):
    async with async_playwright() as playwright:
        try:
            (page, context, browser, task_queue) = await initialize_chromium(
                playwright=playwright
            )
            await page.goto(url, timeout=60000)
            await page_loaded(page)

            print("System is connected to internet => ", is_connected())
            tasks = [task_queue.get() for _ in range(task_queue.qsize())]
            print(f"Waiting for {len(tasks)} tasks!!")
            await asyncio.gather(*tasks)
            print("Wait Finished!!")

            await context.close()
            await browser.close()
        except Exception as e:
            return {"message": f"Something went wrong:: {str(e)}"}


@app.post("/scrap_by_city/{city}")
async def scrap_by_city(city: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_data_by_city, city)
    return {"message": f"Scraping job for {city} has started."}


@app.post("/scrap_by_url")
async def scrap_by_url(url: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_data_by_url, url)
    return {"message": f"Scraping data from {url} has started."}


@app.get("/ping")
async def ping():
    return {"message": "pong"}
