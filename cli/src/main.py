from .ui import wait_for
from .api import test

def main():
    _ = input("TOKEN: ")
    wait_for(test)

if __name__ == "__main__":
    main()
