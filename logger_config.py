import logging
import sys
from typing import Optional
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)
class ColoredFormatter(logging.Formatter):
    base_format = "[%(asctime)s] [%(levelname)s] %(message)s"

    LEVEL_COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
    }

    default_time_format = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelname, "")
        formatter = logging.Formatter(self.base_format, datefmt = self.default_time_format)
        message = formatter.format(record)
        return f"{color}{message}{Style.RESET_ALL}"
    
def get_logger(
        name: Optional[str] = None,
        level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        logger.setLevel(level)
        return logger
    
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger