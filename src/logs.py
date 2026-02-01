"""Logging configuration for the application."""

from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

import structlog
from structlog.dev import ConsoleRenderer


class DailyRotatingFileHandler(RotatingFileHandler):
    """Custom handler for daily log rotation.

    Extends `RotatingFileHandler` to rotate log files based on the current date.

    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        max_bytes: int = 0,
        backup_count: int = 0,
        encoding: str | None = None,
    ):
        """Initialize the handler.

        Parameters
        ----------
        filename : str
            The base name of the log file.
        mode : str, optional
            The file open mode (default is "a").
        max_bytes : int, optional
            The maximum size of a log file before rotation (default is 0).
        backup_count : int, optional
            The number of backup files to keep (default is 0).
        encoding : str or None, optional
            The encoding for the log file (default is None).

        """
        self.base_filename = filename
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        dated_filename = self._get_dated_filename()
        super().__init__(dated_filename, mode, max_bytes, backup_count, encoding)

    def _get_dated_filename(self) -> str:
        """Returns the filename with the current date.

        Returns
        -------
        str
            The dated filename.

        """
        base_path = Path(self.base_filename)
        dated_name = f"{base_path.stem}_{self.current_date}{base_path.suffix}"
        return str(base_path.parent / dated_name)

    def emit(self, record):
        """Override emit to check for day change.

        If the current date is different from the date the handler was
        initialized with, it closes the current log file and opens a
        new one with the updated date.

        Parameters
        ----------
        record : LogRecord
            The log record to emit.

        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        if current_date != self.current_date:
            self.current_date = current_date
            self.close()
            self.baseFilename = self._get_dated_filename()
            if not self.stream:
                self.stream = self._open()

        super().emit(record)


def setup_logger(log_dir: str = "./logs"):
    """Configure the logger.

    Sets up structlog and standard logging with console and daily rotating file handlers.

    Parameters
    ----------
    log_dir : str, optional
        The directory where log files will be stored (default is "./logs").

    Returns
    -------
    structlog.stdlib.BoundLogger
        The configured structlog logger instance.

    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processor=ConsoleRenderer(
            colors=True,
            force_colors=True,
            pad_event_to=30,
            event_key="event",
            sort_keys=False,
        ),
    )

    file_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors
        + [
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.format_exc_info,
        ],
        processor=structlog.processors.JSONRenderer(ensure_ascii=False),
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    file_handler = DailyRotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"), max_bytes=50 * 1024 * 1024
    )
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    return structlog.get_logger()
