import threading
import time

CLEAR = "\033[K"
BOLD = "\033[1m"
RESET = "\033[0m"
BRIGHT_RED = "\033[1;91m"
BRIGHT_GREEN = "\033[1;92m"
BLUE = "\033[1;94m"


def spin(done):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    while not done[0]:
        print(f"\r{chars[i % len(chars)]}", end=CLEAR, flush=True)
        i += 1
        time.sleep(0.1)
    print(f"\r{CLEAR}", end="", flush=True)


def wait_for(fn, *args):
    done = [False]
    t = threading.Thread(target=spin, args=(done,))
    t.start()
    try:
        fn(*args)
    except Exception as e:
        error(e)
    done[0] = True
    t.join()


def input_line(prompt, validate=None):
    while True:
        value = input(f"\r{CLEAR}{BOLD}{BLUE}{prompt}{RESET}: ").strip()
        if validate and not validate(value):
            error(f"Invalid {prompt.lower()}")
            continue
        return value


def error(e):
    print(f"\r{CLEAR}{BRIGHT_RED}{e}{RESET}", flush=True)


def success(s):
    print(f"\r{CLEAR}{BRIGHT_GREEN}{s}{RESET}", flush=True)
