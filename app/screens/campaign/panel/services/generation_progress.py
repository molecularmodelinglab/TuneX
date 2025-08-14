"""
Screen showing experiment generation progress.
"""

from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from app.core.base import BaseWidget
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.cards import Card
from app.shared.components.dialogs import ConfirmationDialog


class GenerationProgressScreen(BaseWidget):
    """Screen displaying experiment generation progress."""

    TITLE_TEXT = "Generating Experiments"
    SUBTITLE_TEXT = "Please wait while we generate your experiments..."
    STATUS_TEXT = "Generating experiments using BayBe..."
    BACK_TO_RUNS_TEXT = "Back to Runs"
    CANCEL_RUN_TEXT = "Cancel Run"
    LAST_UPDATE_TEXT = "Last update: {time}"

    back_to_runs_requested = Signal()
    cancel_run_requested = Signal()
    generation_completed = Signal(list)

    def __init__(self, experiment_count: int, is_first_run: bool = True, parent=None):
        self.experiment_count = experiment_count
        self.is_first_run = is_first_run
        self.start_time = datetime.now()
        self.last_update_time = datetime.now()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_last_update_display)
        self.update_timer.start(60000)

        super().__init__(parent)

    def _setup_widget(self):
        """Setup the progress screen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(30)

        self.progress_card = self._create_progress_card()
        main_layout.addWidget(self.progress_card)

    def _create_progress_card(self) -> QWidget:
        """Create the main progress display card."""
        card = Card()
        card.setMinimumSize(600, 400)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_pixmap = self._get_generation_icon_pixmap()
        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel(self.TITLE_TEXT)
        title_label.setObjectName("GenerationTitle")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel(self.SUBTITLE_TEXT)
        subtitle_label.setObjectName("GenerationSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(subtitle_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setObjectName("GenerationProgress")
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel(self.STATUS_TEXT)
        self.status_label.setObjectName("GenerationStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #444; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.last_update_label = QLabel()
        self.last_update_label.setObjectName("LastUpdateLabel")
        self.last_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_update_label.setStyleSheet("color: #888; font-size: 11px;")
        self._update_last_update_display()
        layout.addWidget(self.last_update_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.back_button = SecondaryButton(self.BACK_TO_RUNS_TEXT)
        self.back_button.clicked.connect(self._handle_back_to_runs)
        if self.is_first_run:
            self.back_button.setEnabled(False)
            self.back_button.setStyleSheet("background-color: #ccc; color: #888;")
        button_layout.addWidget(self.back_button)

        button_layout.addStretch()

        self.cancel_button = PrimaryButton(self.CANCEL_RUN_TEXT)
        self.cancel_button.clicked.connect(self._handle_cancel_run)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        return card

    def _get_generation_icon_pixmap(self) -> QPixmap:
        """Create a generation/loading icon pixmap."""
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        font = QFont("Segoe UI Emoji", 25)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚗️")
        painter.end()

        return pixmap

    def _update_last_update_display(self):
        """Update the last update time display."""
        elapsed = datetime.now() - self.last_update_time

        if elapsed < timedelta(minutes=1):
            time_text = "Just now"
        elif elapsed < timedelta(hours=1):
            minutes = int(elapsed.total_seconds() // 60)
            time_text = f"{minutes} min ago"
        else:
            hours = int(elapsed.total_seconds() // 3600)
            time_text = f"{hours} hour{'s' if hours > 1 else ''} ago"

        self.last_update_label.setText(self.LAST_UPDATE_TEXT.format(time=time_text))

    def _handle_back_to_runs(self):
        """Handle back to runs button click."""
        if not self.is_first_run:
            self.back_to_runs_requested.emit()

    def _handle_cancel_run(self):
        """Handle cancel run button click with confirmation."""
        confirmed = ConfirmationDialog.show_confirmation(
            "Cancel Generation",
            f"Are you sure you want to cancel the generation of {self.experiment_count} experiments?",
            "Yes, Cancel",
            "No, Continue",
            self,
        )

        if confirmed:
            self.cancel_run_requested.emit()

    def update_status(self, status_text: str):
        """Update the status text."""
        self.status_label.setText(status_text)
        self.last_update_time = datetime.now()
        self._update_last_update_display()

    def set_progress(self, value: int, maximum: int = 100):
        """Set determinate progress."""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)

    def complete_generation(self, experiments: list):
        """Complete the generation process."""
        self.update_timer.stop()
        self.generation_completed.emit(experiments)

    def get_panel_buttons(self):
        """Return empty list as buttons are handled internally."""
        return []
