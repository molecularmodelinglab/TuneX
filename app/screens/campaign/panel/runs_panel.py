from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt,  Signal
from PySide6.QtGui import QFont, QPixmap, QPainter
from app.core.base import BaseWidget
from app.shared.components.cards import EmptyStateCard
from app.shared.components.buttons import PrimaryButton


class RunsPanel(BaseWidget):
    """Panel for the 'Runs' tab."""

    new_run_requested = Signal()
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

    def _create_empty_state(self):
        icon_pixmap = self._get_clock_icon_pixmap()
        empty_state = EmptyStateCard(
            primary_message="No runs yet",
            secondary_message="Generate your first run to start experimenting",
            icon_pixmap=icon_pixmap,
        )
        self.main_layout.addWidget(empty_state)

    def _get_clock_icon_pixmap(self) -> QPixmap:
        """Get a clock icon pixmap."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 48))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🕐")
        painter.end()
        
        return pixmap
    
    def _create_buttons_section(self) -> QWidget:
        """Create buttons specific to the Runs panel."""
        buttons_widget = QWidget()
        layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addStretch()
        
        generate_button = PrimaryButton("Generate New Run")
        generate_button.clicked.connect(self.new_run_requested.emit) # Emit its own signal
        layout.addWidget(generate_button)
        
        return buttons_widget