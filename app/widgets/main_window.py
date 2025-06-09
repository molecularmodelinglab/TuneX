"""
This is a placeholder MainWindow class to allow application startup.
The structure and class name can be changed by the person implementing the main screen.
"""

from PySide6.QtWidgets import QMainWindow
from app.widgets.campaign.create.create_campaign_window import CreateCampaignWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuneX")
        # TODO: Replace this stub with the actual main screen implementation.
        self.create_campaign_window = CreateCampaignWindow()
        self.setCentralWidget(self.create_campaign_window)
