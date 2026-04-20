from .ui import wait_for, input_line
from .api import health
from .app import App

def main():

    # init app
    app = App()
    app.get_url()

    # check health
    wait_for(health, app)

if __name__ == "__main__":
    main()
