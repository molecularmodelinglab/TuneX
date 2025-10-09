import logging
import sys

from PySide6.QtWidgets import QApplication

from app.logging_config import setup_application_logging
from app.main_application import MainApplication

APPLICATION_NAME = "BASIL"


def main():
    setup_application_logging(app_name=APPLICATION_NAME)

    logger = logging.getLogger(__name__)
    logger.info("BASIL Starting")

    try:
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName(APPLICATION_NAME)
        app.setApplicationVersion("0.0.1")
        app.setOrganizationName("MML - UNC")

        logger.info("Qt Application created successfully")

        # Create and show main application window
        window = MainApplication()
        window.show()
        logger.info("Main application window initialized and shown")
        sys.exit(app.exec())

    except Exception:
        logger.critical("Critical startup error", exc_info=True)
        sys.exit(1)
