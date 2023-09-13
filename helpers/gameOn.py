from helpers.bbUtils import *
import requests
import requests_cache
from . import StoreFront
from bs4 import BeautifulSoup

from selenium import webdriver
from cache_to_disk import cache_to_disk

import time

requests_cache.install_cache('demo_cache')

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}


@cache_to_disk()
def getScrollingWebsite(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome()

    driver.get(url)

    SCROLL_PAUSE_TIME = 5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    page_source = driver.page_source

    return page_source


class GameOn(StoreFront):
    storeName: str
    urls: list[str]

    def __init__(self):
        return super().__init__("GameOn", [
            "https://www.game-on.no/categories/softgun-kuler-gass-og-diverse?categories%5B%5D=1785&priceLow=53&priceHigh=3799&sort=products_sort_order-asc&filter_by_host=",
            "https://www.game-on.no/categories/softgun-kuler-gass-og-diverse?categories%5B%5D=1786&priceLow=53&priceHigh=3799&sort=products_sort_order-asc&filter_by_host=",
            "https://www.game-on.no/categories/softgun-kuler-gass-og-diverse?categories%5B%5D=1783&priceLow=53&priceHigh=3799&sort=products_sort_order-asc&filter_by_host=",
            "https://www.game-on.no/categories/softgun-kuler-gass-og-diverse?categories%5B%5D=1784&priceLow=53&priceHigh=3799&sort=products_sort_order-asc&filter_by_host="
        ])

    def getProductPages(self) -> {list[BeautifulSoup]}:
        soups = []
        for url in self.urls:
            gon = getScrollingWebsite(url)
            soup = BeautifulSoup(gon, 'html.parser')
            soups.append(soup)
            print(f"Got Product Page {url}")
        return soups

    def getProductSoupLinkList(self, soups: list[BeautifulSoup]) -> {list[BeautifulSoup], list[str]}:
        productLinks = []
        productSoups = []
        for soup in soups:
            results = soup.findAll(
                "div", class_="product_box_title_row text-center")
            for div in results:
                child = div.find("a")
                pageUrl = child.get('href')
                productLinks.append(pageUrl)
                print(f"Got Product Link {pageUrl}")

            for link in productLinks:
                page = requests.get(link, headers=header)
                soup = BeautifulSoup(page.content, 'html.parser')
                productSoups.append(soup)
                print(f"Got Product Soup {link}")
        return productSoups, productLinks

    def getProductName(self, soup: BeautifulSoup) -> str:
        return soup.find("h1", class_="product-title-v1").text

    def getProductPrice(self, soup: BeautifulSoup) -> float:
        return textToPrice(soup.find("span", class_="product-price products_price").text)

    def getProductDescription(self, soup: BeautifulSoup) -> str:
        description = soup.find("div", id="collapse-A")
        texts = description.find_all(text=True)
        desc = ""
        for item in texts:
            desc += item
        return desc
