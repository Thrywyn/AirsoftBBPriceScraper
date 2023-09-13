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


class AirsoftBoden(StoreFront):
    def __init__(self):
        return super().__init__("AirsoftBoden", [
            "https://www.airsoftboden.no/butikk/kuler-gass/0-20g-0-23g",
            "https://www.airsoftboden.no/butikk/kuler-gass/0-25g-0-28g",
            "https://www.airsoftboden.no/butikk/kuler-gass/0-30g-0-32g",
            "https://www.airsoftboden.no/butikk/kuler-gass/0-36g-0-45g",])

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
                "a", class_="productlist__product-wrap neutral-link equal-height-column-innerwrap content-bg")
            for item in results:
                pageUrl = "https://www.airsoftboden.no" + item.get('href')
                productLinks.append(pageUrl)

            for link in productLinks:
                page = requests.get(link, headers=header)
                soup = BeautifulSoup(page.content, 'html.parser')
                productSoups.append(soup)
        return productSoups, productLinks

    def getProductName(self, soup):
        return soup.find("h1", class_="product__title").text

    def getProductPrice(self, soup):
        return textToPrice(soup.find("span", class_="price__display").text)

    def getProductDescription(self, soup):
        return soup.find("p", class_="product__ingress").text

    def getProductWeight(self, soup):
        return textToWeight(self.getProductName(soup))

    def getProductBio(self, soup):
        return textToBio(self.getProductDescription(soup))
