from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseWidget
from app.shared.components.buttons import DangerButton, PrimaryButton, SecondaryButton


class ParametersPanel(BaseWidget):
    """Panel for the 'Parameters' tab."""

    def _setup_widget(self):
        """Setup the parameters panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Placeholder content
        label = QLabel("Parameters View Content")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(label)

    def get_panel_buttons(self):
        """Return buttons specific to this panel."""
        edit_button = PrimaryButton("Edit Parameters")
        # edit_button.clicked.connect(self.parameters_edited.emit)
        return [edit_button]