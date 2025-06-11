import sys
from PySide6.QtWidgets import QApplication
from app.main_application import MainApplication

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("TuneX")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("MML - UNC")
    
    # Create and show main application window
    window = MainApplication()
    window.show()
    
    sys.exit(app.exec())
