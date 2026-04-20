from .ui import input_line, error, success
from .utils import is_valid_url


class App:
    def __init__(self, BASE_URL=None, API_KEY=None):
        self.url = BASE_URL
        self.api_key = API_KEY

    def get_url(self):
        self.url = input_line("URL", is_valid_url)

    def get_api_key(self):
        if not self.url:
            self.get_url()
        self.api_key = input_line("API KEY")

    def auth(self):
        if not self.url:
            self.get_url()
        if not self.api_key:
            self.get_api_key()
        success("Authenticated")
        return True
