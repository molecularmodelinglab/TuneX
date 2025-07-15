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

    def _setup_widget(self):
        """Setup the panel's UI by creating and arranging its components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create and add the empty state card
        self._create_empty_state()
        
        # Create and add the action buttons
        self.main_layout.addWidget(self._create_buttons_section())

    def _create_empty_state(self):
        icon_pixmap = self._get_clock_icon_pixmap()
        print(icon_pixmap)
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
        painter.setFont(QFont("Segoe UI Emoji", 25))
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
        layout.addStretch()
        
        return buttons_widget