import requests

from .app import App


def health(app: App):
    res = requests.get(f"{app.url}/health")
    return res


def process(app: App):
    pass
