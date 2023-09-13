from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from helpers.bbUtils import *
from bs4 import BeautifulSoup


class StoreFront(ABC):
    storeName: str
    urls: list[str]

    @abstractmethod
    def __init__(self, storeName: str, urls: list[str]):
        self.storeName = storeName
        self.urls = urls

    @abstractmethod
    def getProductPages(self) -> {list[BeautifulSoup]}:
        pass

    @abstractmethod
    def getProductSoupLinkList(self, soups: list[BeautifulSoup]) -> {list[BeautifulSoup], list[str]}:
        pass

    @abstractmethod
    def getProductName(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def getProductPrice(self, soup: BeautifulSoup) -> float:
        pass

    @abstractmethod
    def getProductDescription(self, soup: BeautifulSoup) -> str:
        pass

    def getProductWeight(self, soup: BeautifulSoup) -> float:
        return textToWeight(self.getProductName(soup))

    def getProductBio(self, soup: BeautifulSoup) -> bool:
        return textToBio(self.getProductDescription(soup)) or textToBio(self.getProductName(soup))

    def getProductAmount(self, soup: BeautifulSoup) -> int:
        try:
            return textToAmount(self.getProductName(soup))
        except:
            return textToAmount(self.getProductDescription(soup))
