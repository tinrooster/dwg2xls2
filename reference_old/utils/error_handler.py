from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    def show_error(parent, message, exception=None):
        logger.error(f"{message}: {str(exception) if exception else ''}")
        QMessageBox.critical(parent, "Error", message)

    @staticmethod
    def show_warning(parent, message):
        logger.warning(message)
        QMessageBox.warning(parent, "Warning", message)

    @staticmethod
    def show_info(parent, message):
        logger.info(message)
        QMessageBox.information(parent, "Information", message)
