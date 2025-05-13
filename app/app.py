import sys
from PySide6.QtWidgets import QApplication
from app.widgets.main_window import MainWindow  # TODO: replace if the interface changes

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
