from PySide6.QtWidgets import (
    QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.core.base import BaseWidget
from app.shared.components.cards import EmptyStateCard


class RunsPanel(BaseWidget):
    """Panel for the 'Runs' tab."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # This can be replaced with a table of runs later
        self.empty_state = EmptyStateCard(
            primary_message="No runs yet",
            secondary_message="Generate your first run to start experimenting",
        )
        layout.addWidget(self.empty_state)


    def _create_buttons_section(self):
        pass