import re
import sys
import asyncio
from time import sleep
import traceback
from typing import Any, List, Dict
import socket
from playwright.async_api import (
    async_playwright,
    Playwright,
    Page,
    Response,
    TimeoutError as PlaywrightTimeout,
    BrowserContext,
)
from utility import format_price, relative_time_to_timestamp
from init_db import (
    init_db,
    insert_failure_data,
    insert_popularity_trends,
    insert_area_trends,
    insert_queries_data,
    insert_property_data,
)

REMOTE_SERVER = "one.one.one.one"


def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception:
        pass
    return False


def handle_error(function_name: str, error: Exception, url: str):
    desc = f"{function_name}::Error: {error} url => {url}"
    print(desc, file=sys.stderr)
    insert_failure_data(desc=desc, url=url)
    print("System is connected to the internet => ", is_connected())
    traceback.print_exc()
    sleep(10)


print("System is connected to internet => ", is_connected())

try:
    init_db()
except Exception as err:
    handle_error("init_db", err, "")


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
                has_text=re.compile("^find$", re.IGNORECASE)
            )
            await find_button.click(timeout=timeout)
            break
        except PlaywrightTimeout:
            await asyncio.sleep(30)
            retries += 1
        except Exception as e:
            handle_error("search_city", e, page.url)
            break
    if retries == max_retries:
        desc = f"Maximum retries reached. search_city failed for city: {city}"
        print(desc)
        insert_failure_data(desc=desc, url=page.url)
    print("!!!search_city finished!!!")


async def handle_response(response: Response):
    if (
        "queries" not in response.url
        and "areaTrends" not in response.url
        and "popularityTrends" not in response.url
    ):
        return
    print("data url ===>>> ", response.url)
    try:
        json_data = await response.json()
        print("json_data ===>>>", json_data)
        if "areaTrends" in response.url:
            insert_area_trends(json_data)

        if "popularityTrends" in response.url:
            # Popularity Trends
            insert_popularity_trends(json_data)

        if "queries" in response.url:

            for results in json_data["results"]:
                try:
                    hits = results["hits"]
                    if len(hits) == 0:
                        print("hits is empty array!!!!!")
                        return
                    insert_queries_data(hits)
                except Exception as e:
                    handle_error(
                        "handle_response::inserting_queries", e, "handle_response"
                    )
                    continue

    except Exception as e:
        handle_error("handle_response", e, "handle_response")


async def fetch_all_text_contents(page: Page, label: str):
    elements = await page.get_by_label(label).all_text_contents()
    return " ".join(elements).strip()


async def fetch_details(page: Page):
    return await page.get_by_label("property details").get_by_role("listitem").all()


async def process_page(new_page: Page, h2: List[str]):
    print("******Inside process_page function*****")
    try:
        header, details, desc = await asyncio.gather(
            fetch_all_text_contents(new_page, "Property header"),
            fetch_details(new_page),
            fetch_all_text_contents(new_page, "property description"),
        )
        # header = " ".join(await new_page.get_by_label("Property header")
        # .all_text_contents()).strip()
        # details = await new_page.get_by_label("property details").get_by_role("listitem").all()
        # desc = " ".join(await new_page.get_by_label
        # ("property description").all_text_contents()).strip()

        # in_active_banner_count = await new_page.get_by_label("Inactive property banner").count()
        # if in_active_banner_count > 0:
        #     print("in-active property found!")
        #     continue
        async def fetch_text_contents(element):
            return "".join(await element.all_text_contents()).strip()

        key_value_obj: Dict[str, Any] = {
            "header": " ".join(h2) + "\n" + header,
            "desc": desc,
        }
        for li in details:
            print("all locators in li ==> ", await li.locator("span").all())
            key, value = await asyncio.gather(
                fetch_text_contents(li.locator(
                    "span").first), fetch_text_contents(li)
            )
            value = value.replace(key, "")
            # key = "".join(await li.locator("span").first.all_text_contents()).strip()
            # value = "".join(await li.all_text_contents()).replace(key, "").strip()
            if key.lower() == "price":
                key_value_obj[key.lower()] = format_price(value)
            elif key.lower() == "added":
                key_value_obj[key.lower()] = relative_time_to_timestamp(value)
            else:
                key_value_obj[key.split(
                    "(")[0].lower().replace(" ", "_")] = value
        insert_property_data(key_value_obj)
    except Exception as e:
        handle_error("process_page", e, new_page.url)


async def get_page_html_data(
    base_url: str, current_page: Page, context: BrowserContext
):
    max_retries = 4
    retries = 0
    while retries < max_retries:
        try:
            article_tags = await current_page.locator("article").all()
            print("Number of article tags => ", len(article_tags))
            for a in article_tags:
                print("<article> ==>>>> ", a)
                h2 = await a.locator("h2").all_text_contents()
                print("h2 => ", h2)
                if len(h2) > 0:
                    href = await a.locator("a").first.get_attribute(
                        "href", timeout=60000
                    )
                    if href is None:
                        print("No href found in link!")
                        continue
                    new_page = await context.new_page()
                    await new_page.goto(base_url + href, timeout=60000)
                    await process_page(new_page=new_page, h2=h2)
                    await new_page.close()
            break

        except PlaywrightTimeout:
            await asyncio.sleep(30)
            retries += 1
        except Exception as e:
            handle_error("get_page_html_data", e, current_page.url)
            break
    if retries == max_retries:
        desc = f"Maximum retries reached. get_page_html_data failed for url: {current_page.url}"
        print(desc)
        insert_failure_data(desc=desc, url=current_page.url)
    print("!!get_page_html_data Finished!!")


async def page_loaded(p: Page):
    print("page_Loaded called")
    context = p.context
    base_url = "/".join(p.url.split("/")[:3])
    max_retries = 4
    retries = 0
    while retries < max_retries:
        try:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            while True:
                count = (
                    await p.get_by_role("link")
                    .filter(has=p.get_by_title(re.compile("^Next$", re.IGNORECASE)))
                    .count()
                )
                if count > 0:
                    next_page = p.get_by_role("link").filter(
                        has=p.get_by_title(re.compile("^Next$", re.IGNORECASE))
                    )
                else:
                    next_page = None
                await get_page_html_data(
                    base_url=base_url, current_page=p, context=context
                )
                if count > 0 and next_page is not None:
                    next_url = await next_page.get_attribute("href", timeout=60000)
                    if next_url is None:
                        print("No next_url found!!")
                        break
                    dot = next_url.rfind(".")
                    hyphen = next_url.rfind("-")
                    page_no = next_url[hyphen + 1: dot]
                    # ONLY 1st 2 Pages!
                    # if int(page_no) >= 1:
                    #     break
                    await p.goto(base_url + next_url)
                    await asyncio.sleep(10)
                else:
                    break

            print(
                "end of loop!!",
            )
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            break
        except PlaywrightTimeout:
            await asyncio.sleep(30)
            retries += 1
        except Exception as e:
            handle_error("page_loaded", e, p.url)
            break

    if retries == max_retries:
        desc = f"Maximum retries reached. page_loaded failed for url: {p.url}"
        print(desc)
        insert_failure_data(desc=desc, url=p.url)
    print("!!page_Loaded Finished!!")


# Crawl website


async def crawl_website(page: Page, url: str, links: List[str], depth: int):
    print(f"Visiting: {url}, currently at depth {depth}")
    await page.goto(url, timeout=60000)
    for link in links:
        links_to_visit = await page.locator(
            f'a[href*="{link}"]:link:not([href^="http"])'
        ).all()
        for locator in links_to_visit:
            try:
                href = await locator.get_attribute("href")
                if href is None:
                    continue
                await page.goto(url + href)
                await page_loaded(page)
            except PlaywrightTimeout:
                print(
                    f"crawl_website::Timeout error while getting attribute {locator}",
                    file=sys.stderr,
                )
                print("System is connected to internet => ", is_connected())
                continue
            except Exception as e:
                handle_error("crawl_website", e, page.url)
                continue


# async def track_pages(page: Page):
#     page.on("load", page_loaded)
async def initialize_chromium(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch()
    context = await browser.new_context()

    page = await context.new_page()
    task_queue = asyncio.Queue()
    # input_file = json.load(open("input.json"))

    async def response_handler(response: Response):
        await task_queue.put(await handle_response(response))

    context.on("response", response_handler)
    return (page, context, browser, task_queue)
