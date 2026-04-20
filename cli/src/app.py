from .ui import input_line, error


class App:
    def __init__(self, BASE_URL=None):
        self.url = BASE_URL

    def get_url(self):
        while True:
            url = input_line("CLOUD URL")
            if not url.startswith("http://") and not url.startswith("https://"):
                print(url)
                error("url most start with http:// or https://")
                continue
            self.url = url
            break
