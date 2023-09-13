import re


def removeAllChars(text):
    return re.sub(r"[^0-9]", "", text)


def removeAllExceptDot(text):
    return re.sub(r"[^0-9\.]", "", text)


def textToWeight(text):
    weight = re.search(r"0(\.|,)[0-9]{1,2}\s?g", text)
    weight = weight.group(0)
    return float(weight.replace("g", "").replace(",", "."))


def textToBio(text):
    bio = len(re.findall("bio", text, re.IGNORECASE)) >= 1
    notBio = len(re.findall(r"(ikke\not).{0,10}bio", text, re.IGNORECASE)) >= 1
    if notBio:
        bio = False
    return bio


def textToAmount(text):
    amount = re.search(r"[0-9]{3,5}\s?(stk|kuler|biokuler|pcs)",
                       text, re.IGNORECASE)
    if amount is None:
        amount = re.search(r"[0-9]{4,5}",
                           text, re.IGNORECASE)
    amount = amount.group(0)

    totalAmount = re.search(
        r"totalt.{0,15}[0-9]{3,5}\s?(stk|kuler|biokuler|pcs)", text, re.IGNORECASE)
    if totalAmount is not None:
        if totalAmount.group(0) > amount:
            amount = totalAmount.group(0)

    amount = int(removeAllChars(amount))
    return amount


def textToPrice(text):
    return float(removeAllExceptDot(text.replace(",", ".")))
