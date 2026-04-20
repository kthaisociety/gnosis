import threading
import time

CLEAR = "\033[K"


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
    fn(*args)
    done[0] = True
    t.join()
