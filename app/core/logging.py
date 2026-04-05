import logging
import sys
from logging.handlers import RotatingFileHandler

from pythonjsonlogger.jsonlogger import JsonFormatter


def setup_logging() -> None:
    formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [console_handler, file_handler]

    # заглушаем шумные логи SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
