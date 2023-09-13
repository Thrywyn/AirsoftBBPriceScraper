import os
from cache_to_disk import cache_to_disk
import time
from selenium import webdriver
from prettytable import PrettyTable
import string
import re
from bs4 import BeautifulSoup

# To cache requests
import requests
import requests_cache
requests_cache.install_cache('demo_cache')

# To cache selenium webpages
os.environ['CACHES_DSN'] = 'redis://localhost:6379/0'


@cache_to_disk()
def getScrollingWebsite(url: string):
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


class BB:
    def __init__(self, name: str, weight: float, price: float, link: str, bio: bool, amount: int):
        self.name = name
        self.weight = weight
        self.price = price
        self.link = link
        self.bio = bio
        self.amount = amount
        self.value = self.price / self.amount
        self.pricePerThousands = self.price / self.amount * 1000

    def __str__(self):
        return self.name + " " + str(self.weight) + " " + str(self.price) + " " + self.link + " " + str(self.bio) + " " + str(self.amount) + " " + str(self.value) + " " + str(self.pricePerThousands)


ab1 = "https://www.airsoftboden.no/butikk/kuler-gass/0-20g-0-23g"
ab2 = "https://www.airsoftboden.no/butikk/kuler-gass/0-25g-0-28g"
ab3 = "https://www.airsoftboden.no/butikk/kuler-gass/0-30g-0-32g"
ab4 = "https://www.airsoftboden.no/butikk/kuler-gass/0-36g-0-45g"

sp = "https://sandefjordpaintball.no/softgun-airsoft/kuler"

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}

airsoftBodenCategories = [ab1,
                          ab2, ab3, ab4]

page = requests.get(ab1, headers=header)
soup = BeautifulSoup(page.content, 'html.parser')


def textToWeight(text):
    weight = re.search(r"0(\.|,)[0-9]{1,2}g", text)
    weight = weight.group(0)
    return float(weight.replace("g", "").replace(",", "."))


def textToBio(text):
    bio = len(re.findall("bio", text, re.IGNORECASE)) >= 1
    return bio


def textToAmount(text):
    amount = re.search(r"[0-9]{3,5}\s?(stk|kuler|biokuler)",
                       text, re.IGNORECASE)
    if amount is None:
        amount = re.search(r"[0-9]{4,5}",
                           text, re.IGNORECASE)
    amount = amount.group(0)
    amount = int(amount.replace("stk", "").replace(
        "kuler", "").replace("bio", ""))
    return amount


def textToPrice(text):
    return float(text.replace("kr", "").replace(",", "."))


def abItemGetter(soup):
    results = soup.findAll(
        "a", class_="productlist__product-wrap neutral-link equal-height-column-innerwrap content-bg")
    links = []
    for item in results:
        pageUrl = "https://www.airsoftboden.no" + item.get('href')
        links.append(pageUrl)
    soups = []
    for link in links:
        page = requests.get(link, headers=header)
        soup = BeautifulSoup(page.content, 'html.parser')
        soups.append(soup)
    return soups, links


def abNameGetter(soup):
    return soup.find("h1", class_="product__title").text


def abPriceGetter(soup):
    return textToPrice(soup.find("span", class_="price__display").text)


def abDescriptionGetter(soup):
    return soup.find("p", class_="product__ingress").text


def abWeightGetter(soup):
    return textToWeight(abNameGetter(soup))


def abBioGetter(soup):
    return textToBio(abDescriptionGetter(soup))


def abAmountGetter(soup):
    return textToAmount(abNameGetter(soup))


def spItemGetter(soup):
    results = soup.findAll(
        "li", class_="item product product-item")
    links = []
    for item in results:
        pageUrl = item.find("a").get('href')
        links.append(pageUrl)
    soups = []
    for link in links:
        page = requests.get(link, headers=header)
        soup = BeautifulSoup(page.content, 'html.parser')
        soups.append(soup)
    return soups, links


def spNameGetter(soup):
    return soup.find("span", class_="base").text


def spPriceGetter(soup):
    return textToPrice(soup.find("span", class_="price").text)


def spDescriptionGetter(soup):
    div = soup.find("div", class_="product attribute description")
    p = div.find("p")
    if p is None:
        p = div.find("div", class_="value")
    return p.text


def spWeightGetter(soup):
    return textToWeight(spNameGetter(soup))


def spBioGetter(soup):
    return textToBio(spDescriptionGetter(soup))


def spAmountGetter(soup):
    return textToAmount(spNameGetter(soup))


def bbListParser(site: string, url: str, itemsGetter: callable, nameGetter: callable, priceGetter: callable, descriptionGetter: callable, weightGetter: callable, bioGetter: callable, amountGetter: callable):
    page = requests.get(url, headers=header)
    soup = BeautifulSoup(page.content, 'html.parser')

    soups, links = itemsGetter(soup)

    bbs = []

    for soup, link in zip(soups, links):
        try:
            name = nameGetter(soup)
            price = priceGetter(soup)
            weight = weightGetter(soup)
            description = descriptionGetter(soup)
            bio = bioGetter(soup)
            amount = amountGetter(soup)

            thisBB = BB(name, weight, price, link, bio, amount)
            bbs.append(thisBB)
        except Exception as error:
            print("Error parsing " + link)
            print("An exception occurred:", error)
    return bbs


allResults = []

for airsoftBoden in airsoftBodenCategories:
    res = bbListParser("airsoftBoden", airsoftBoden, abItemGetter, abNameGetter,
                       abPriceGetter, abDescriptionGetter, abWeightGetter, abBioGetter, abAmountGetter)
    allResults.extend(res)

res = bbListParser("sandefjordPaintball", sp, spItemGetter, spNameGetter,
                   spPriceGetter, spDescriptionGetter, spWeightGetter, spBioGetter, spAmountGetter)
allResults.extend(res)


allResults.sort(key=lambda x: x.value)

table = PrettyTable()

table.field_names = ["Name", "Weight",
                     "Price", "Link", "Bio", "Amount", "Value", "Price per 1000"]

for bb in allResults:
    table.add_row([bb.name, bb.weight, bb.price,
                  bb.link, bb.bio, bb.amount, bb.value, bb.pricePerThousands])

print(table)

gon = getScrollingWebsite(
    "https://www.game-on.no/categories/softgun-kuler-gass-og-diverse?categories%5B%5D=1785&priceLow=53&priceHigh=3799&sort=products_sort_order-asc&filter_by_host=")


soup = BeautifulSoup(gon, 'html.parser')

results = soup.findAll("div", class_="product_box_title_row text-center")

print(results)

# # Filter for only bio bbs
# bioResults = list(filter(lambda x: x.bio, allResults))
# bioTable = PrettyTable()
# bioTable.field_names = ["Name", "Weight",
#                         "Price", "Link", "Bio", "Amount", "Value", "Price per 1000"]
# for bb in bioResults:
#     bioTable.add_row([bb.name, bb.weight, bb.price,
#                       bb.link, bb.bio, bb.amount, bb.value, bb.pricePerThousands])
# print(bioTable)
