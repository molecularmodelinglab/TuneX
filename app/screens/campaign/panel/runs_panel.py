from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.core.base import BaseWidget
from app.shared.components.buttons import PrimaryButton
from app.shared.components.cards import EmptyStateCard


class RunsPanel(BaseWidget):
    """Panel for the 'Runs' tab."""

    PRIMARY_MESSAGE = "No runs yet"
    SECONDARY_MESSAGE = "Generate your first run to start experimenting"
    PIXMAP_FONT = QFont("Segoe UI Emoji", 25)
    NEW_RUNS_BUTTON_TEXT = "Generate New Run"

    new_run_requested = Signal()

    def _setup_widget(self):
        """Setup the panel's UI by creating and arranging its components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create and add the empty state card
        self._create_empty_state()

    def _create_empty_state(self):
        icon_pixmap = self._get_clock_icon_pixmap()
        print(icon_pixmap)
        empty_state = EmptyStateCard(
            primary_message=self.PRIMARY_MESSAGE,
            secondary_message=self.SECONDARY_MESSAGE,
            icon_pixmap=icon_pixmap,
        )
        self.main_layout.addWidget(empty_state)
        self.main_layout.addStretch()

    def _get_clock_icon_pixmap(self) -> QPixmap:
        """Get a clock icon pixmap."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(self.PIXMAP_FONT)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🕐")
        painter.end()

        return pixmap

    def get_panel_buttons(self):
        """Return buttons specific to this panel."""
        generate_button = PrimaryButton(self.NEW_RUNS_BUTTON_TEXT)
        generate_button.clicked.connect(self.new_run_requested.emit)
        return [generate_button]
