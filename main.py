from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
import asyncio
from os import environ, getcwd
from sys import exit
from playwright.async_api import (
    async_playwright,
)
from scrape import search_city, page_loaded, initialize_chromium, is_connected
from lock_file import create_lock, is_locked, remove_lock

baseUrl = environ.get("BASE_URL")

if baseUrl is None:
    print("BASE_URL is missing in env file!")
    exit(1)

CRONJOB_SCRIPT_PATH = getcwd() + "/cronjob.py"


async def launch_chronjob():
    try:
        await asyncio.create_subprocess_exec("python3", CRONJOB_SCRIPT_PATH)
    except Exception as e:
        print(f"Error running the script: {e}")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await launch_chronjob()
    yield
    remove_lock()


app = FastAPI(lifespan=lifespan)


async def scrape_data_by_city(city: str):
    if is_locked():
        print("Job is already running. Exiting this instance.")
        return

    create_lock()
    async with async_playwright() as playwright:
        context = None
        browser = None
        try:
            (page, context, browser) = await initialize_chromium(playwright=playwright)
            await page.goto(baseUrl, timeout=60000)
            await search_city(city=city, page=page, purpose="Buy", property="Homes")
            await page_loaded(page)

            print("System is connected to internet => ", is_connected())
            await asyncio.sleep(600)
            print("Wait Finished!!")

        except Exception as e:
            return {"message": f"Something went wrong:: {str(e)}"}
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
            remove_lock()


async def scrape_data_by_url(url: str):
    if is_locked():
        print("Job is already running. Exiting this instance.")
        return

    create_lock()
    async with async_playwright() as playwright:
        context = None
        browser = None
        try:
            (page, context, browser) = await initialize_chromium(playwright=playwright)
            await page.goto(url, timeout=60000)
            await page_loaded(page)

            print("System is connected to internet => ", is_connected())
            await asyncio.sleep(600)
            print("Wait Finished!!")

            await context.close()
            await browser.close()
        except Exception as e:
            return {"message": f"Something went wrong:: {str(e)}"}
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
            remove_lock()


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
