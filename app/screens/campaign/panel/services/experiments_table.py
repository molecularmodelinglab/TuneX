"""
Screen for displaying and editing experiment results in a table format.
"""

from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QLineEdit, QStyledItemDelegate
)

from app.core.base import BaseWidget
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.cards import Card
from app.models.campaign import Campaign

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
    
    back_to_runs_requested = Signal()
    save_results_requested = Signal(list)
    new_run_requested = Signal()

    def __init__(self, experiments: List[Dict[str, Any]], campaign: Campaign, run_number: int = 1, parent=None):
        self.experiments = experiments.copy()
        self.campaign = campaign
        self.run_number = run_number
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
        
        instructions = QLabel("💡 Fill in the target values after conducting your experiments")
        instructions.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(instructions)
        
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
        
        new_run_button = PrimaryButton(self.GENERATE_NEW_RUN_TEXT)
        new_run_button.clicked.connect(self.new_run_requested.emit)
        button_layout.addWidget(new_run_button)
        
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
        param_columns = []
        target_columns = []

        for key in all_experiment_keys:
            if key in campaign_target_names:
                target_columns.append(key)
            else:
                param_columns.append(key)

        for target in self.campaign.targets:
            if target.name not in target_columns:
                target_columns.append(target.name)

        all_columns = param_columns + target_columns
        
        self.table.setRowCount(len(self.experiments))
        self.table.setColumnCount(len(all_columns))
        self.table.setHorizontalHeaderLabels(all_columns)
        
        for row, experiment in enumerate(self.experiments):
            for col, param_name in enumerate(param_columns):
                value = experiment.get(param_name, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                item.setBackground(Qt.GlobalColor.lightGray)
                self.table.setItem(row, col, item)
        
        large_input_delegate = LargeInputDelegate()
        for row in range(len(self.experiments)):
            for col_idx, target in enumerate(self.campaign.targets):
                col = len(param_columns) + col_idx
                existing_value = experiment.get(target.name, "")
                item = QTableWidgetItem(str(existing_value) if existing_value is not None else "")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
                self.table.setItemDelegateForColumn(col, large_input_delegate)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Style the headers to differentiate parameter vs target columns
        # header = self.table.horizontalHeader()
        # for i in range(len(param_columns)):
        #     header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def _handle_save_results(self):
        """Handle saving the results with target values."""
        # Extract target values from table
        param_columns = list(self.experiments[0].keys()) if self.experiments else []
        updated_experiments = []
        
        for row in range(self.table.rowCount()):
            experiment = self.experiments[row].copy()
            
            for col_idx, target in enumerate(self.campaign.targets):
                col = len(param_columns) + col_idx
                item = self.table.item(row, col)
                if item and item.text().strip():
                    try:
                        value = float(item.text().strip())
                        experiment[target.name] = value
                    except ValueError:
                        experiment[target.name] = item.text().strip()
                else:
                    experiment[target.name] = None
            
            updated_experiments.append(experiment)
        
        self.save_results_requested.emit(updated_experiments)

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the table."""
        if not self.experiments:
            return False
            
        param_columns = list(self.experiments[0].keys())
        
        for row in range(self.table.rowCount()):
            for col_idx, target in enumerate(self.campaign.targets):
                col = len(param_columns) + col_idx
                item = self.table.item(row, col)
                if item and item.text().strip():
                    return True
        return False

    def get_panel_buttons(self):
        """Return empty list as buttons are handled internally."""
        return []
