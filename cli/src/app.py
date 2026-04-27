from dotenv import load_dotenv
import os

from .ui import input_line, error, success
from .utils import is_valid_url
from .api import auth as api_auth

from lib.utils.log import get_logger

load_dotenv()
logger = get_logger(__name__)

PATH_CREDENTIALS = f"{os.path.dirname(os.path.abspath(__file__))}/credentials"


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
        if not self.read_credentials():
            if not self.url:
                self.get_url()
            if not self.api_key:
                self.get_api_key()
        if api_auth(self.url, self.api_key):
            self.store_credentials()
            success("Authenticated")
            return True
        error("Failed to authenticate")
        return False

    def read_credentials(self) -> bool:
        try:
            with open(PATH_CREDENTIALS, "r", encoding="utf-8") as f:
                lines = f.readlines()
                url = lines[0].strip()
                api_key = lines[1].strip()
                if url and api_key:
                    self.url = url
                    self.api_key = api_key
                    return True
                return False
        except Exception as e:
            logger.warning("Failed to read credentials from store")
            self.url = None
            self.api_key = None
            return False

    def store_credentials(self):
        with open(PATH_CREDENTIALS, "w", encoding="utf-8") as f:
            f.write(f"{self.url}\n{self.api_key}\n")
