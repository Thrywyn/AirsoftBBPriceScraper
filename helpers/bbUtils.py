import re


def removeAllChars(text):
    return re.sub(r"[^0-9]", "", text)


def textToWeight(text):
    weight = re.search(r"0(\.|,)[0-9]{1,2}\s?g", text)
    weight = weight.group(0)
    return float(weight.replace("g", "").replace(",", "."))


def textToBio(text):
    bio = len(re.findall("bio", text, re.IGNORECASE)) >= 1
    return bio


def textToAmount(text):
    amount = re.search(r"[0-9]{3,5}\s?(stk|kuler|biokuler|pcs)",
                       text, re.IGNORECASE)
    if amount is None:
        amount = re.search(r"[0-9]{4,5}",
                           text, re.IGNORECASE)
    amount = amount.group(0)
    amount = int(removeAllChars(amount))
    return amount


def textToPrice(text):
    return float(text.replace("kr", "").replace(",", "."))
