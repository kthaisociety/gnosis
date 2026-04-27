import requests


def health(url: str):
    res = requests.get(f"{url}/health")
    return res


# TODO
def process(url: str, image, pdf):
    pass


def auth(url: str, api_key: str):
    res = requests.get(f"{app.url}/auth/{app.api_key}")
    return res == True
