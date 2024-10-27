import sys
import logging
from PyQt6.QtWidgets import QApplication

# Use absolute imports for package distribution
from dwg2xls.utils.logger import setup_logger
from dwg2xls.gui.main_window import MainWindow

def main():
    setup_logger()
    logger = logging.getLogger('AutoCADExcelTool')
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    logger.info('Application started')
    sys.exit(app.exec())

def main_debug():
    setup_logger(level=logging.DEBUG)
    main()

if __name__ == '__main__':
    main()
