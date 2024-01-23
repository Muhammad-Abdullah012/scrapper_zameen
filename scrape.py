import re
import asyncio
import traceback
from typing import Any
from utility import format_price, relative_time_to_timestamp
from playwright.async_api import async_playwright, Playwright, Page, Response, TimeoutError, BrowserContext
from init_db import init_db, insert_popularity_trends, insert_area_trends, insert_queries_data, insert_property_data

with open("errors.logs.txt", mode="a") as errorFile:
    try:
        init_db()
    except Exception as e:
        print(f"init_db::Error: {e}", file=errorFile)

    async def search_city(city: str, page: Page, timeout=60000):
        max_retries = 4
        retries = 0
        while retries < max_retries:
            try:
                locator = page.get_by_label("city filter")
                await locator.click(timeout=timeout)
                button = page.get_by_role("listbox").last
                print("button ==> ", button)
                b = button.locator("button", has_text=city)
                print("b ==> ", b)
                await b.click(timeout=timeout)

                find_button = page.get_by_role("button").filter(
                    has_text=re.compile("^find$", re.IGNORECASE))
                await find_button.click(timeout=timeout)
                break
            except TimeoutError:
                await asyncio.sleep(30)
                retries += 1
            except Exception as e:
                print(f"search_city::Error: {e}",
                      file=errorFile)
                break
        if retries == max_retries:
            print(
                f"Maximum retries reached. search_city failed for city: {city}")
        print("!!!search_city finished!!!")

    async def handle_response(response: Response):
        if "queries" not in response.url and "areaTrends" not in response.url and "popularityTrends" not in response.url:
            return
        print("data url ===>>> ", response.url)
        try:
            json_data = await response.json()
            print("json_data ===>>>", json_data)
            if "areaTrends" in response.url:
                insert_area_trends(json_data)
                pass
            if "popularityTrends" in response.url:
                # Popularity Trends
                insert_popularity_trends(json_data)

            if "queries" in response.url:
                pass
                for results in json_data["results"]:
                    try:
                        hits = results["hits"]
                        if len(hits) == 0:
                            print("hits is empty array!!!!!")
                            return
                        insert_queries_data(hits)
                    except Exception as e:
                        print(
                            f"handle_response::inserting_queries::Error: {e}", file=errorFile)
                        continue

        except Exception as e:
            print(f"handle_response::Error: {e}",
                  file=errorFile)

    async def get_page_html_data(base_url: str, current_page: Page, context: BrowserContext):
        max_retries = 4
        retries = 0
        while retries < max_retries:
            try:
                article_tags = await current_page.locator("article").all()
                print("Number of article tags => ", len(
                    article_tags))
                for a in article_tags:
                    print("<article> ==>>>> ", a)
                    h2 = await a.locator("h2").all_text_contents()
                    print("h2 => ", h2)
                    if len(h2) > 0:
                        href = await a.locator("a").first.get_attribute("href", timeout=60000)
                        new_page = await context.new_page()
                        if href is None:
                            print("No href found in link!")
                            continue
                        await new_page.goto(base_url + href, timeout=60000)
                        ul = []
                        header = " ".join(await new_page.get_by_label("Property header").all_text_contents()).strip()
                        details = await new_page.get_by_label("property details").get_by_role("listitem").all()
                        desc = " ".join(await new_page.get_by_label("property description").all_text_contents()).strip()

                        # in_active_banner_count = await new_page.get_by_label("Inactive property banner").count()
                        # if in_active_banner_count > 0:
                        #     print("in-active property found!")
                        #     continue
                        key_value_obj: dict[str, Any] = {
                            "header": " ".join(h2) + "\n" + header, "desc": desc
                        }
                        for li in details:
                            print("all locators in li ==> ", await li.locator("span").all())
                            key = "".join(await li.locator("span").first.all_text_contents()).strip()
                            value = "".join(await li.all_text_contents()).replace(key, "").strip()
                            print("key => ", key, " value => ", value)
                            if key.lower() == "price":
                                key_value_obj[key.lower()] = format_price(
                                    value)
                            elif key.lower() == "added":
                                key_value_obj[key.lower(
                                )] = relative_time_to_timestamp(value)
                            else:
                                key_value_obj[key.split(
                                    "(")[0].lower().replace(" ", "_")] = value

                        insert_property_data(key_value_obj)
                        await new_page.close()
                        print("ul ==> ", ul)
                break

            except TimeoutError:
                await asyncio.sleep(30)
                retries += 1
            except Exception as e:
                print(f"get_page_html_data::Error: {e}", file=errorFile)
                traceback.print_exc()
                break
        if retries == max_retries:
            print(
                f"Maximum retries reached. get_page_html_data failed for url: {current_page.url}")
        print("!!get_page_html_data Finished!!")

    async def page_loaded(p: Page):
        print("page_Loaded called")
        context = p.context
        base_url = '/'.join(p.url.split("/")[:3])
        max_retries = 4
        retries = 0
        while retries < max_retries:
            try:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                while True:
                    count = await p.get_by_role("link").filter(
                        has=p.get_by_title(re.compile("^Next$", re.IGNORECASE))).count()
                    if count > 0:
                        next_page = p.get_by_role("link").filter(
                            has=p.get_by_title(re.compile("^Next$", re.IGNORECASE)))
                    else:
                        next_page = None
                    await get_page_html_data(base_url=base_url, current_page=p, context=context)
                    if count > 0 and next_page is not None:
                        next_url = await next_page.get_attribute("href")
                        print("next_url ==> ", file=open("next_url.txt", "a"))
                        if next_url is None:
                            print("No next_url found!!",
                                  file=open("next_url.txt", "a"))
                            break
                        dot = next_url.rfind(".")
                        hyphen = next_url.rfind("-")
                        page_no = next_url[hyphen+1:dot]
                        # ONLY 1st 2 Pages!
                        # if int(page_no) >= 1:
                        #     break
                        await p.goto(base_url + next_url)
                        await asyncio.sleep(10)
                    else:
                        break

                print("end of loop!!", )
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                break
            except TimeoutError:
                await asyncio.sleep(30)
                retries += 1
            except Exception as e:
                print(f"page_loaded::Error: {e}",
                      file=errorFile)
                traceback.print_exc()
                break

        if retries == max_retries:
            print(
                f"Maximum retries reached. page_loaded failed for url: {p.url}")
        print("!!page_Loaded Finished!!")
    # Crawl website

    async def crawl_website(page: Page, url: str, links: list[str], depth: int):
        print(f"Visiting: {url}, currently at depth {depth}")
        await page.goto(url, timeout=60000)
        for link in links:
            links_to_visit = await page.locator(f'a[href*="{link}"]:link:not([href^="http"])').all()
            for locator in links_to_visit:
                try:
                    href = await locator.get_attribute("href")
                    if href is None:
                        continue
                    await page.goto(url + href)
                    await page_loaded(page)
                except TimeoutError:
                    print(
                        f"crawl_website::Timeout error while getting attribute {locator}", file=errorFile)
                    continue
                except Exception as e:
                    print(f"crawl_website::Error: {e}",
                          file=errorFile)
                    continue

    # async def track_pages(page: Page):
    #     page.on("load", page_loaded)

    async def run(playwright: Playwright):
        chromium = playwright.chromium
        browser = await chromium.launch()
        context = await browser.new_context()

        page = await context.new_page()
        task_queue = asyncio.Queue()
        # input_file = json.load(open("input.json"))

        async def response_handler(response: Response):
            await task_queue.put(await handle_response(response))

        context.on("response", response_handler)
        # page.on("load", page_loaded)
        # await crawl_website(page, "https://www.zameen.com", links=input_file["links"], depth=0, browser_context=context)
        # await page.goto("https://www.zameen.com", timeout=0)
        # await page.goto("https://www.zameen.com/Homes/Islamabad-3-159.html", timeout=0)
        # await page_loaded(page)
        cities = ["islamabad", "rawalpindi", "lahore", "karachi"]
        for city in cities:
            await page.goto("https://www.zameen.com", timeout=0)
            await search_city(city=city, page=page)
            await page_loaded(page)

        tasks = [task_queue.get() for _ in range(task_queue.qsize())]
        print(f"Waiting for {len(tasks)} tasks!!")
        await asyncio.gather(*tasks)
        print("Wait Finished!!")

        await context.close()
        await browser.close()

    async def main():
        async with async_playwright() as playwright:
            try:
                await run(playwright)
            except Exception as e:
                print(f"main::Error: {e}", file=errorFile)

    asyncio.run(main())
