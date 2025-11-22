import logging
import os
import sys

_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def _resolve_level() -> int:
    level_str = (os.getenv("LOGGING_LEVEL") or "INFO").upper()
    return _LEVELS.get(level_str, logging.INFO)


def _build_base_logger() -> logging.Logger:
    logger = logging.getLogger("gnosis")
    if logger.handlers:
        return logger
    logger.setLevel(_resolve_level())
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logger.level)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(handler)
    logger.propagate = False  # Important to add, I read it somewhere
    return logger


_BASE = _build_base_logger()


def get_logger(name: str | None = None) -> logging.Logger:
    if not name or name == "__main__":
        return _BASE
    return _BASE.getChild(name)


def set_level(level: int | str) -> None:
    lvl = _LEVELS.get(str(level).upper(), level) if isinstance(level, str) else level
    _BASE.setLevel(lvl)
    for h in _BASE.handlers:
        h.setLevel(lvl)


__all__ = ["get_logger", "set_level"]
