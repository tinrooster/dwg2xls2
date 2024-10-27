from mss import mss
from pathlib import Path
import logging
import sys
import os
import win32gui
import win32con
from PyQt5.QtCore import QtCore

logger = logging.getLogger('AutoCADExcelTool.Screenshot')

class ScreenshotUtil:
    def __init__(self):
        self.screenshot_dir = Path(__file__).parent.parent / "resources" / "help" / "images"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.sct = mss()

    def capture_area(self, name, area=None):
        """
        Capture screenshot of specified area
        area: dict with keys 'top', 'left', 'width', 'height'
        """
        try:
            filename = self.screenshot_dir / f"{name}.png"
            if area:
                screenshot = self.sct.grab(area)
            else:
                screenshot = self.sct.grab(self.sct.monitors[0])
            self.sct.shot(output=str(filename))
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")
            return False

    def capture_window(self, name, window_title):
        """
        Capture screenshot of specific window by title
        Requires win32gui on Windows
        """
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                area = {
                    "top": rect[1],
                    "left": rect[0],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                }
                return self.capture_area(name, area)
            return False
        except ImportError:
            logger.error("win32gui not available for window capture")
            return False

    def capture_widget(self, name, widget):
        """
        Capture screenshot of specific Qt widget
        """
        try:
            geometry = widget.geometry()
            pos = widget.mapToGlobal(QtCore.QPoint(0, 0))
            area = {
                "top": pos.y(),
                "left": pos.x(),
                "width": geometry.width(),
                "height": geometry.height()
            }
            return self.capture_area(name, area)
        except Exception as e:
            logger.error(f"Widget capture failed: {str(e)}")
            return False
