import logging
import logging.config


COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
}

RESET = "\033[0m"
# we have imported the logging.Formatter  class from logging and  added the basic new functionality
# ther is override happening in the default format() function which was
# we used super() so that rest of the part of the format function of Formatter class will be used in it ,  so that
# our formatting of other thing  will work


class ColorFormatter(logging.Formatter):
    def format(self, record):
        level_name = record.levelname
        color = COLORS.get(level_name, "")
        record.levelname = f"{color}{level_name}{RESET}"
        return super().format(record)


def setup_logging(verbose=False, quiet=False, log_to_file=False):
    if quiet:
        level = "ERROR"
    elif verbose:
        level = "DEBUG"
    else:
        level = "INFO"

    handlers = ["console"]
    if log_to_file:
        handlers.append("file")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ColorFormatter,
                "format": "%(asctime)s %(levelname)s %(message)s",
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "colored",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "standard",
                "filename": "organize.log",
                "mode": "a",
            },
        },
        "root": {"level": "DEBUG", "handlers": handlers},
    }

    logging.config.dictConfig(LOGGING_CONFIG)
