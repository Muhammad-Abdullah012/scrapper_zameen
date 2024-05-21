from os import environ
import dotenv
import asyncio
from playwright.async_api import (
    async_playwright,
    Playwright,
)
from scrape import (
    initialize_chromium,
    search_city,
    page_loaded,
    is_connected,
    handle_error,
)

dotenv.load_dotenv()


async def run(playwright: Playwright):
    baseUrl = environ.get("BASE_URL")
    if baseUrl is None:
        print("BASE_URL is missing in env file!")
        return

    (page, context, browser) = await initialize_chromium(playwright=playwright)
    try:
        cities = ["islamabad", "rawalpindi", "lahore", "karachi"]
        properties = ["Homes", "Plots", "Commercial"]
        purpose = ["Buy", "Rent"]
        for city in cities:
            for p in purpose:
                for property in properties:
                    await page.goto(baseUrl, timeout=0)
                    await search_city(
                        city=city, page=page, purpose=p, property=property
                    )
                    await page_loaded(page)
                    print("waiting for 10 seconds")
                    await asyncio.sleep(10)
                    print("wait finished")

        # await search_city(city=city, page=page)
        # await page_loaded(page)

        print("System is connected to internet => ", is_connected())
        await asyncio.sleep(600)
        print("Wait Finished!!")
    except Exception as e:
        handle_error("run", e, "run")
    finally:
        if "context" in locals():
            await context.close()
        if "browser" in locals():
            await browser.close()


async def run_main():
    async with async_playwright() as playwright:
        try:
            await run(playwright)
        except Exception as e:
            handle_error("main", e, "main")


def main():
    if asyncio.get_event_loop().is_running():
        loop = asyncio.get_event_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(run_main())


main()
