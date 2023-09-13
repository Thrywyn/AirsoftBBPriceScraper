from helpers import StoreFront, AirsoftBoden, SandefjordPaintball, GameOn
from colorama import Fore, Back, Style

import requests_cache
import requests
import os
from cache_to_disk import cache_to_disk
import time
from selenium import webdriver
from prettytable import PrettyTable
import string
import re
from bs4 import BeautifulSoup
import sys
import traceback

from colorama import init

init(autoreset=True)

# Enable debugging
debugPrints = True

# Enable advanced debugging
debugPrintsAdvanced = False


# To cache requests
requests_cache.install_cache('demo_cache')

# To cache selenium webpages
os.environ['CACHES_DSN'] = 'redis://localhost:6379/0'


class BB:
    def __init__(self, name: str, weight: float, price: float, link: str, bio: bool, amount: int):
        self.name = name.strip()
        self.weight = weight
        self.price = price
        self.link = link
        self.bio = bio
        self.amount = amount
        self.value = self.price / self.amount
        self.pricePerThousands = self.price / self.amount * 1000
        self. bbsPerKilo = 1000 / self.weight
        self.pricePerKilo = self.value * self.bbsPerKilo

    def __str__(self):
        return self.name + " " + str(self.weight) + " " + str(self.price) + " " + self.link + " " + str(self.bio) + " " + str(self.amount) + " " + str(self.value) + " " + str(self.pricePerThousands)


def bbListParser(storeFront: StoreFront):

    productPageSoups = storeFront.getProductPages()

    soups, links = storeFront.getProductSoupLinkList(productPageSoups)

    bbs = []
    for soup, link in zip(soups, links):
        try:
            name = storeFront.getProductName(soup)
            price = storeFront.getProductPrice(soup)
            weight = storeFront.getProductWeight(soup)
            description = storeFront.getProductDescription(soup)
            bio = storeFront.getProductBio(soup)
            amount = storeFront.getProductAmount(soup)

            thisBB = BB(name, weight, price, link, bio, amount)
            bbs.append(thisBB)
            print(f"Sucessfully parsed: {link}")
        except Exception as error:
            if debugPrints:
                print(Fore.RED + "Error parsing " + link)
                if debugPrintsAdvanced:
                    print("An exception occurred:", error)
                    print(traceback.format_exc())

    return bbs


allResults = []

# Scrape Websites
allResults.extend(bbListParser(AirsoftBoden()))
print(Fore.GREEN + f"Finished scraping AirsoftBoden")
allResults.extend(bbListParser(SandefjordPaintball()))
print(Fore.GREEN + f"Finished scraping SandefjordPaintball")
allResults.extend(bbListParser(GameOn()))
print(Fore.GREEN + f"Finished scraping GameOn")

print(f"Found {len(allResults)} results")

# Filter for only BIO
# allResults = list(filter(lambda x: x.bio, allResults))

# Sort
allResults.sort(key=lambda x: x.pricePerKilo)


# Pretty print table
table = PrettyTable()
table.field_names = ["Name", "Weight",
                     "Price", "Bio", "Amount", "Value", "Price per 1000", "Price per Kilo", "Link"]

for bb in allResults:
    table.add_row([bb.name, bb.weight, bb.price,
                   bb.bio, bb.amount, '{0:.2f}'.format(bb.value), '{0:.2f}'.format(bb.pricePerThousands), '{0:.2f}'.format(bb.pricePerKilo), bb.link])

print(table)
