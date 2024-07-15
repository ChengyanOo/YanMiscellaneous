import json
import random
import tempfile
from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
import time
from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.common.keys import Keys  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # type: ignore


def write_to_json(data: list, filename: str):
    """Append a list of elements to a JSON file ensuring valid array format."""
    try:
        with open(filename, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []
    except json.JSONDecodeError:
        existing_data = []

    existing_data.extend(data)
    
    with open(filename, 'w') as file:
        json.dump(existing_data, file)

def parse_page(soup: BeautifulSoup) -> (bool, list):
    """Parse the HTML soup of a page and extract details for each shop."""
    results = []
    web_href = None
    shop_details_blocks = soup.find_all("div", class_="shop-details-block")
    website_link = soup.find("a", class_="b-shop-website")
    if website_link and "href" in website_link.attrs:
        web_href = website_link["href"].strip()

    for block in shop_details_blocks:
        result = {
            "S_NAME_E": None,
            "Mall_E": None,
            "SHOP_NO_E": None,
            "Tel": None,
            "Website": None,
            "BIZ_HRS": None,
            "Cat_E": None,
        }

        # Shop name and category
        shop_name = block.find_previous("h1", class_="b-shop-name")
        category = block.find_previous("span", class_="b-shop-type")
        if shop_name:
            result["S_NAME_E"] = shop_name.text.strip()
        if category:
            result["Cat_E"] = category.text.strip()

        result["Website"] = web_href

        # Mall name
        mall_name = block.find("img", src=lambda x: x and "getting-there.svg" in x)
        if mall_name:
            result["Mall_E"] = mall_name.find_next_sibling(text=True).strip()

        # Shop number
        shop_no = block.find("img", src=lambda x: x and "unit-icon.svg" in x)
        if shop_no:
            result["SHOP_NO_E"] = shop_no.find_next_sibling(text=True).strip()

        # Telephone
        phone_div = block.find("img", src=lambda x: x and "phone-icon.svg" in x)
        if phone_div:
            phone_link = phone_div.find_next(
                "a", href=lambda x: x and x.startswith("tel:")
            )
            if phone_link:
                result["Tel"] = phone_link.text.strip()

        # Opening hours
        opening_hours_span = soup.find("span", class_="b-shop-opening-hour")
        if opening_hours_span:
            hours = []
            for p in opening_hours_span.find_all("p"):
                if p.text.strip():
                    hours.append(p.text.strip())
            result["BIZ_HRS"] = ", ".join(hours)

        if any(value is not None for value in result.values()):
            results.append(result)

    if results:
        return True, results
    return False, []

with open("./shops.html", "r") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "html.parser")
links = soup.find_all("a", href=True)
shop_links = [
    link["href"] for link in links if "/en/shops/shop?shopName=" in link["href"]
]
shop_links = ["https://www.fareastmalls.com.sg" + link for link in shop_links]

working_links, failed_links, success_links = [], [], []
driver = webdriver.Chrome()
working_links = shop_links

try:
    for link in shop_links:
        driver.get(link)
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_html = driver.page_source
            soup = BeautifulSoup(page_html, "html.parser")
            # process the page
            is_success, result = parse_page(soup)
            if is_success:
                print(f"result: {result}")
                write_to_json(result, "data.json")
                success_links.append(link)
            else:
                failed_links.append(link)
        except TimeoutException:
            print(f"Timeout while loading page: {link}")

        time.sleep(random.uniform(1, 3))

finally:
    print("Failed links: ", failed_links)
    print("Success links: ", success_links)
    driver.quit()

