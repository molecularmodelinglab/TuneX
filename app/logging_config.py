"""
Logging configuration for the application.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths


def _create_formatter() -> logging.Formatter:
    """Create the standard log formatter."""
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def _setup_console_handler(logger: logging.Logger, level: int) -> None:
    """Add console handler to logger."""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(_create_formatter())
    logger.addHandler(console_handler)


def _setup_app_log_handler(
    logger: logging.Logger, log_path: Path, level: int, max_size_mb: int, backup_count: int
) -> None:
    """Add main application log handler."""
    app_log_file = log_path / "basil.log"
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file, maxBytes=max_size_mb * 1024 * 1024, backupCount=backup_count
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(_create_formatter())
    logger.addHandler(app_handler)


def _setup_error_log_handler(logger: logging.Logger, log_path: Path, max_size_mb: int) -> None:
    """Add error-only log handler."""
    error_log_file = log_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=(max_size_mb // 2) * 1024 * 1024, backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(_create_formatter())
    logger.addHandler(error_handler)


def _get_log_directory(app_name: str) -> str:
    """Get platform-appropriate directory for log files"""
    config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    app_config_dir = os.path.join(config_dir, app_name)
    log_dir = os.path.join(app_config_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def setup_application_logging(
    app_name: str,
    app_log_level: int = logging.DEBUG,
    console_log_level: int = logging.INFO,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """Configure logging for the application."""
    log_dir = _get_log_directory(app_name)

    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Setup handlers
    _setup_console_handler(logger, console_log_level)
    _setup_app_log_handler(logger, log_path, app_log_level, max_file_size_mb, backup_count)
    _setup_error_log_handler(logger, log_path, max_file_size_mb)

    # Log success
    app_logger = logging.getLogger(__name__)
    app_logger.info(f"Logging configured in: {log_path.absolute()}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module/component."""
    return logging.getLogger(name)
