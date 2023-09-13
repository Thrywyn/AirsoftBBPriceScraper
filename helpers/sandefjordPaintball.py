from helpers.bbUtils import *
import requests
import requests_cache
from . import StoreFront
from bs4 import BeautifulSoup


# To cache requests
requests_cache.install_cache('demo_cache')

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}


class SandefjordPaintball(StoreFront):
    def __init__(self):
        return super().__init__("SandefjordPaintball", [
            "https://sandefjordpaintball.no/softgun-airsoft/kuler",])

    def getProductPages(self) -> {list[BeautifulSoup]}:
        soups = []
        for url in self.urls:
            page = requests.get(url, headers=header)
            soup = BeautifulSoup(page.content, 'html.parser')
            soups.append(soup)
        return soups

    def getProductSoupLinkList(self, soups: list[BeautifulSoup]) -> {list[BeautifulSoup], list[str]}:
        productLinks = []
        productSoups = []
        for soup in soups:

            results = soup.findAll(
                "li", class_="item product product-item")
            for item in results:
                pageUrl = item.find("a").get('href')
                productLinks.append(pageUrl)
            for link in productLinks:
                page = requests.get(link, headers=header)
                soup = BeautifulSoup(page.content, 'html.parser')
                productSoups.append(soup)
        return productSoups, productLinks

    def getProductName(self, soup):
        return soup.find("span", class_="base").text

    def getProductPrice(self, soup):
        return textToPrice(soup.find("span", class_="price").text)

    def getProductDescription(self, soup):
        divDescription = soup.find(
            "div", class_="product attribute description")
        p = divDescription.findAll("p")
        desc = ""
        for item in p:
            desc += item.text
        return desc

    def getProductWeight(self, soup):
        return textToWeight(self.getProductName(soup))

    def getProductBio(self, soup):
        return textToBio(self.getProductDescription(soup))
