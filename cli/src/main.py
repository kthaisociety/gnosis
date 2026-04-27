import sys

from .ui import wait_for
from .api import health
from .app import App


def main():

    # init app
    app = App()
    app.auth()

    # check health
    wait_for(health, app.url)


if __name__ == "__main__":
    main()
