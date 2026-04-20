from .ui import wait_for, input_line
from .api import health
from .app import App

def main():

    # init app
    BASE_URL = input_line("URL")
    app = App(BASE_URL)

    # check health
    wait_for(health, app)

if __name__ == "__main__":
    main()
