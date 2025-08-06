import os
import shutil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QTextEdit, QVBoxLayout, QWidget

from app.core.base import BaseWidget
from app.screens.start.components.campaign_loader import CampaignLoader
from app.shared.components.buttons import DangerButton, PrimaryButton
from app.shared.utils.export_campaign import CampaignExporter


class SettingsPanel(BaseWidget):
    """Panel for the 'Settings' tab with campaign settings form."""

    # Signals for various actions
    campaign_renamed = Signal(str)
    campaign_description_updated = Signal(str)
    campaign_deleted = Signal()
    data_exported = Signal()
    home_requested = Signal()

    # UI Constants
    PANEL_TITLE = "Campaign Settings"
    NAME_LABEL = "Campaign name"
    DESCRIPTION_LABEL = "Description"
    NAME_PLACEHOLDER = "Enter campaign name"
    DESCRIPTION_PLACEHOLDER = "Description of the Campaign"

    RENAME_BUTTON_TEXT = "Rename"
    EDIT_BUTTON_TEXT = "Edit"
    DELETE_BUTTON_TEXT = "Delete Campaign"
    HOME_BUTTON_TEXT = "Home"
    EXPORT_BUTTON_TEXT = "Export Data"

    MAIN_MARGINS = (30, 30, 30, 30)
    FORM_SPACING = 20
    BUTTON_SECTION_SPACING = 20
    DESCRIPTION_HEIGHT = 100

    def __init__(self, campaign=None, workspace_path=None, parent=None):
        self.campaign = campaign
        self.workspace_path = workspace_path
        self.campaign_loader = CampaignLoader(workspace_path) if workspace_path else None
        super().__init__(parent)

    def _setup_widget(self):
        """Setup the settings panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*self.MAIN_MARGINS)
        main_layout.setSpacing(25)

        # Panel title
        title_label = QLabel(self.PANEL_TITLE)
        title_label.setObjectName("PanelTitle")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Form section
        form_widget = self._create_form_section()
        main_layout.addWidget(form_widget)

        main_layout.addStretch()
        self._load_campaign_data()

    def _create_form_section(self) -> QWidget:
        """Create the form section with campaign name and description."""
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(self.FORM_SPACING)

        # Campaign name section
        name_section = self._create_name_section()
        name_label = QLabel(self.NAME_LABEL)
        name_label.setObjectName("FormLabel")
        form_layout.addRow(name_label, name_section)

        # Description section
        description_section = self._create_description_section()
        desc_label = QLabel(self.DESCRIPTION_LABEL)
        desc_label.setObjectName("FormLabel")
        form_layout.addRow(desc_label, description_section)

        return form_widget

    def _create_name_section(self) -> QWidget:
        """Create campaign name input with rename button."""
        name_widget = QWidget()
        layout = QHBoxLayout(name_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Name input field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.NAME_PLACEHOLDER)
        self.name_input.setObjectName("FormInput")
        self.name_input.setReadOnly(True)  # Read-only by default
        layout.addWidget(self.name_input)

        # Rename button
        self.rename_button = PrimaryButton(self.RENAME_BUTTON_TEXT)
        self.rename_button.setFixedWidth(120)
        self.rename_button.clicked.connect(self._handle_rename_click)
        layout.addWidget(self.rename_button)

        return name_widget

    def _create_description_section(self) -> QWidget:
        """Create description input with edit button."""
        desc_widget = QWidget()
        layout = QVBoxLayout(desc_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Description text area
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(self.DESCRIPTION_PLACEHOLDER)
        self.description_input.setFixedHeight(self.DESCRIPTION_HEIGHT)
        self.description_input.setObjectName("FormInput")
        self.description_input.setReadOnly(True)  # Read-only by default
        layout.addWidget(self.description_input)

        # Edit button (right-aligned)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.edit_button = PrimaryButton(self.EDIT_BUTTON_TEXT)
        self.edit_button.setFixedWidth(100)
        self.edit_button.clicked.connect(self._handle_edit_click)
        button_layout.addWidget(self.edit_button)
        layout.addLayout(button_layout)

        return desc_widget

    def _handle_rename_click(self):
        """Handle rename button click - toggle edit mode for name."""
        if self.name_input.isReadOnly():
            # Switch to edit mode
            self.name_input.setReadOnly(False)
            self.name_input.setFocus()
            self.name_input.selectAll()
            self.rename_button.setText("Save")
        else:
            # Save and switch back to read-only mode
            new_name = self.name_input.text().strip()
            if new_name and self.campaign:
                old_name = self.campaign.name
                self.campaign.name = new_name

                if self._save_campaign_changes():
                    self.campaign_renamed.emit(new_name)
                    print(f"Campaign renamed from '{old_name}' to '{new_name}'")
                else:
                    self.campaign.name = old_name
                    self.name_input.setText(old_name)
                    print("Failed to save campaign name change")

            self.name_input.setReadOnly(True)
            self.rename_button.setText(self.RENAME_BUTTON_TEXT)

    def _handle_edit_click(self):
        """Handle edit button click - toggle edit mode for description."""
        if self.description_input.isReadOnly():
            # Switch to edit mode
            self.description_input.setReadOnly(False)
            self.description_input.setFocus()
            self.edit_button.setText("Save")
        else:
            # Save and switch back to read-only mode
            new_description = self.description_input.toPlainText().strip()
            if self.campaign:
                old_description = self.campaign.description
                self.campaign.description = new_description
                if self._save_campaign_changes():
                    self.campaign_description_updated.emit(new_description)
                    print("Campaign description updated")
                else:
                    self.campaign.description = old_description
                    self.description_input.setPlainText(old_description)
                    print("Failed to save campaign description change")

            self.description_input.setReadOnly(True)
            self.edit_button.setText(self.EDIT_BUTTON_TEXT)

    def _load_campaign_data(self):
        """Load existing campaign data into the form fields."""
        if self.campaign:
            self.name_input.setText(self.campaign.name or "")
            self.description_input.setPlainText(self.campaign.description or "")

    def _handle_export_click(self):
        """Handle export button click - export campaign data to CSV."""
        CampaignExporter.export_campaign_to_csv(self.campaign, self)

    def _handle_delete_click(self):
        """Handle delete campaign button click."""
        if not self.campaign:
            QMessageBox.warning(self, "Delete Error", "No campaign to delete.")
            return

        campaign_name = self.campaign.name or "Unnamed Campaign"

        reply = QMessageBox.question(
            self,
            "Confirm Delete Campaign",
            f"Are you sure you want to delete the campaign '{campaign_name}'?\n\n"
            "This action will permanently delete:\n"
            "• Campaign data file\n"
            "• Campaign folder and all contents\n"
            "• All experiment results\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,  # Default to No for safety
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self._delete_campaign_files():
                    QMessageBox.information(
                        self, "Campaign Deleted", f"Campaign '{campaign_name}' has been successfully deleted."
                    )
                    # Emit signal to return to home screen
                    self.campaign_deleted.emit()
                else:
                    QMessageBox.critical(
                        self,
                        "Delete Error",
                        f"Failed to delete campaign '{campaign_name}'. Some files may still exist.",
                    )
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"An error occurred while deleting the campaign:\n{str(e)}")

    def _delete_campaign_files(self) -> bool:
        """Delete campaign files and folders. Returns True if successful."""
        if not self.campaign or not self.workspace_path:
            return False

        try:
            success = True
            campaign_name = self.campaign.name or "unnamed_campaign"

            json_filename = f"{campaign_name}.json"
            json_path = os.path.join(self.workspace_path, json_filename)

            if os.path.exists(json_path):
                try:
                    os.remove(json_path)
                    print(f"Deleted campaign file: {json_path}")
                except Exception as e:
                    print(f"Failed to delete campaign file {json_path}: {e}")
                    success = False

            campaign_folder = os.path.join(self.workspace_path, campaign_name)

            if os.path.exists(campaign_folder) and os.path.isdir(campaign_folder):
                try:
                    shutil.rmtree(campaign_folder)
                    print(f"Deleted campaign folder: {campaign_folder}")
                except Exception as e:
                    print(f"Failed to delete campaign folder {campaign_folder}: {e}")
                    success = False

            if self.campaign_loader:
                try:
                    self.campaign_loader.delete_campaign(self.campaign)
                except Exception as e:
                    print(f"Failed to remove campaign from loader: {e}")
                    # Don't set success to False here as the files might still be deleted
            return success

        except Exception as e:
            print(f"Error during campaign deletion: {e}")
            return False

    def _save_campaign_changes(self) -> bool:
        """Save campaign changes to JSON file. Returns True if successful."""
        if not self.campaign_loader or not self.campaign:
            return False

        try:
            self.campaign_loader.update_campaign(self.campaign)
            return True
        except Exception as e:
            print(f"Error saving campaign: {e}")
            return False

    def get_panel_buttons(self):
        """Return buttons specific to this panel."""
        buttons = []

        delete_button = DangerButton(self.DELETE_BUTTON_TEXT)
        delete_button.clicked.connect(self._handle_delete_click)
        buttons.append(delete_button)

        export_button = PrimaryButton(self.EXPORT_BUTTON_TEXT)
        export_button.clicked.connect(self._handle_export_click)
        buttons.append(export_button)

        return buttons

    def update_campaign_data(self, campaign):
        """Update the panel with new campaign data."""
        self.campaign = campaign
        self._load_campaign_data()

    def set_campaign(self, campaign):
        """Set the campaign and update the form fields."""
        self.campaign = campaign
        self._load_campaign_data()

    def set_workspace_path(self, workspace_path: str):
        """Set the workspace path and update the campaign loader."""
        self.workspace_path = workspace_path
        self.campaign_loader = CampaignLoader(workspace_path) if workspace_path else None
