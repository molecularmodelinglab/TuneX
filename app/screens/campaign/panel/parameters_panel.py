from PySide6.QtWidgets import (
    QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.core.base import BaseWidget

class ParametersPanel(BaseWidget):
    """Panel for the 'Parameters' tab."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Parameters View Content")
        label.setFont(QFont("Arial", 18))
        layout.addWidget(label)
    
    def _create_buttons_section(self):
        pass