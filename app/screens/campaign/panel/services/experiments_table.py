"""
Screen for displaying and editing experiment results in a table format.
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.base import BaseWidget
from app.models.campaign import Campaign
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.cards import Card


class LargeInputDelegate(QStyledItemDelegate):
    """Custom delegate for larger input fields in table cells."""

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setPlaceholderText("Enter value...")
        # Make the input field larger
        editor.setMinimumHeight(35)
        editor.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value is not None:
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.ItemDataRole.EditRole)


class ExperimentsTableScreen(BaseWidget):
    """Screen for displaying experiment results in an editable table."""

    TITLE_TEXT = "Experiment Results"
    SUBTITLE_TEXT = "Review your generated experiments and add target values"
    BACK_TO_RUNS_TEXT = "Back to Runs"
    SAVE_RESULTS_TEXT = "Save Results"
    GENERATE_NEW_RUN_TEXT = "Generate New Run"
    DEFAULT_INSTRUCTION_TEXT = "💡 Fill in target values for each experiment before saving."

    back_to_runs_requested = Signal()
    save_results_requested = Signal(list)

    def __init__(self, experiments: List[Dict[str, Any]], campaign: Campaign, run_number: int = 1, parent=None):
        self.experiments = experiments.copy()
        self.campaign = campaign
        self.run_number = run_number
        self._param_columns: List[str] = []
        self._target_columns: List[str] = []
        self.original_experiments = experiments.copy()

        super().__init__(parent)

    def _setup_widget(self):
        """Setup the experiments table screen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        header_widget = self._create_header()
        main_layout.addWidget(header_widget)

        table_card = self._create_table_card()
        main_layout.addWidget(table_card)

    def _create_header(self) -> QWidget:
        """Create the header section."""
        header_widget = QWidget()
        layout = QVBoxLayout(header_widget)
        layout.setSpacing(5)

        title_label = QLabel(f"{self.TITLE_TEXT} - Run {self.run_number}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        subtitle_text = f"{self.SUBTITLE_TEXT} ({len(self.experiments)} experiments)"
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(subtitle_label)

        return header_widget

    def _create_table_card(self) -> QWidget:
        """Create the main table display card."""
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.table = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table)

        self.instructions_label = QLabel(self.DEFAULT_INSTRUCTION_TEXT)
        self.instructions_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(self.instructions_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        back_button = SecondaryButton(self.BACK_TO_RUNS_TEXT)
        back_button.clicked.connect(self.back_to_runs_requested.emit)
        button_layout.addWidget(back_button)

        button_layout.addStretch()

        save_button = PrimaryButton(self.SAVE_RESULTS_TEXT)
        save_button.clicked.connect(self._handle_save_results)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        return card

    def _setup_table(self):
        """Setup the experiments table."""
        if not self.experiments:
            return

        all_experiment_keys = set()
        for experiment in self.experiments:
            all_experiment_keys.update(experiment.keys())

        campaign_target_names = {target.name for target in self.campaign.targets}
        param_columns: List[str] = []
        target_columns: List[str] = []

        for key in all_experiment_keys:
            if key in campaign_target_names:
                target_columns.append(key)
            else:
                param_columns.append(key)

        for target in self.campaign.targets:
            if target.name not in target_columns:
                target_columns.append(target.name)

        self._param_columns = param_columns
        self._target_columns = target_columns

        all_columns = self._param_columns + self._target_columns

        self.table.setRowCount(len(self.experiments))
        self.table.setColumnCount(len(all_columns))
        self.table.setHorizontalHeaderLabels(all_columns)

        for row, experiment in enumerate(self.experiments):
            for col, param_name in enumerate(self._param_columns):
                value = experiment.get(param_name, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                item.setBackground(Qt.GlobalColor.lightGray)
                self.table.setItem(row, col, item)

        large_input_delegate = LargeInputDelegate()
        for target_idx, target in enumerate(self.campaign.targets):
            col = len(self._param_columns) + target_idx
            self.table.setItemDelegateForColumn(col, large_input_delegate)

        for row, experiment in enumerate(self.experiments):
            for target_idx, target in enumerate(self.campaign.targets):
                col = len(self._param_columns) + target_idx
                existing_value = experiment.get(target.name, "")
                item = QTableWidgetItem(str(existing_value) if existing_value is not None else "")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(50)

    def _handle_save_results(self):
        """Handle saving the results with target values."""
        # Extract target values from table
        if not self.experiments:
            return

        updated_experiments: List[Dict[str, Any]] = []

        for row in range(self.table.rowCount()):
            original = self.original_experiments[row].copy()
            experiment = original

            for target_idx, target in enumerate(self.campaign.targets):
                col = len(self._param_columns) + target_idx
                item = self.table.item(row, col)
                if not item:
                    experiment[target.name] = None
                    continue
                text = item.text().strip()
                if not text:
                    experiment[target.name] = None
                    continue
                try:
                    experiment[target.name] = float(text)
                except ValueError:
                    experiment[target.name] = text

            updated_experiments.append(experiment)

        self.experiments = updated_experiments
        self.original_experiments = updated_experiments.copy()

        self.save_results_requested.emit(updated_experiments)
        self._show_save_confirmation()

    def _show_save_confirmation(self):
        """Show visual feedback that results were saved."""
        if hasattr(self, "instructions_label"):
            original_text = self.instructions_label.text()
            self.instructions_label.setText("✅ Results saved successfully!")
            self.instructions_label.setStyleSheet("color: #28a745; font-size: 12px; padding: 10px; font-weight: bold;")

            from PySide6.QtCore import QTimer

            QTimer.singleShot(2000, lambda: self._reset_instructions_text(original_text))

    def _reset_instructions_text(self, original_text):
        """Reset instructions text back to original."""
        if hasattr(self, "instructions_label"):
            self.instructions_label.setText(original_text)
            self.instructions_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the table."""
        if not self.experiments:
            return False

        for row in range(self.table.rowCount()):
            original = self.original_experiments[row]
            for target_idx, target in enumerate(self.campaign.targets):
                col = len(self._param_columns) + target_idx
                item = self.table.item(row, col)
                current_text = item.text().strip() if item else ""
                original_value = original.get(target.name, None)
                if original_value is None:
                    if current_text != "":
                        return True
                else:
                    if str(original_value) != current_text:
                        return True
        return False

    def get_panel_buttons(self):
        """Return empty list as buttons are handled internally."""
        return []
