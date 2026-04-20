import requests


def health(url: str):
    res = requests.get(f"{url}/health")
    return res


# TODO
def process(url: str, image, pdf):
    pass


# TODO
def auth(url: str, api_key: str):
    # _ = requests.get(f"{app.url}/auth/{app.api_key}")
    return True
