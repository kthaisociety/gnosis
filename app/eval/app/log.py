import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def get_logger(name: str = "eval") -> logging.Logger:
    return logging.getLogger(name)


debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
