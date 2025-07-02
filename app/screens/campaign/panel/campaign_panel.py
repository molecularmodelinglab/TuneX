"""
Base panel screen for a campaign, managing different views via tabs.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QPushButton, QStackedWidget
)
from PySide6.QtGui import QFont

from app.core.base import BaseScreen
from app.models.campaign import Campaign
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.screens.campaign.panel.parameters_panel import ParametersPanel
from app.screens.campaign.panel.runs_panel import RunsPanel
from app.screens.campaign.panel.settings_panel import SettingsPanel


class CampaignPanelScreen(BaseScreen):
    """
    Base screen for the campaign panel.
    Manages navigation between Runs, Parameters, and Settings tabs.
    """

    # Signals
    home_requested = Signal()
    new_run_requested = Signal()

    def __init__(self, campaign: Campaign, parent=None):
        super().__init__(parent)
        self.campaign: Campaign = campaign
        self.tabs = {}
        self._setup_screen()

    def _setup_screen(self):
        """Setup the default campaign screen UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_tab_section())

        # Stacked widget for tab content
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self._create_panels()

        main_layout.addWidget(self._create_home_buttons_section())

    def _create_header(self) -> QWidget:
        """Create the campaign header section."""
        header_widget = QWidget()
        header_widget.setObjectName("CampaignHeader")
        header_widget.setFixedHeight(60)
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # TuneX title
        title_label = QLabel("TuneX")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setObjectName("AppTitle")
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        return header_widget

    def _create_tab_section(self) -> QWidget:
        """Create the tab navigation section."""
        tab_widget = QWidget()
        tab_widget.setObjectName("TabSection")
        
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(20, 20, 20, 0)
        layout.setSpacing(15)
        
        # Campaign name and metadata
        campaign_name = QLabel(self.campaign.name or "My Cool Campaign 1")
        campaign_name.setObjectName("CampaignName")
        campaign_font = QFont()
        campaign_font.setPointSize(18)
        campaign_font.setBold(True)
        campaign_name.setFont(campaign_font)
        
        # Campaign metadata
        param_count = len(self.campaign.parameters) if self.campaign.parameters else "Nan"
        target_names = ", ".join([t.name for t in self.campaign.targets]) or "None"
        metadata_text = f"Created on 25 April, 2025 • {param_count} Parameters • Targets: {target_names}"
        
        metadata_label = QLabel(metadata_text)
        metadata_label.setObjectName("CampaignMetadata")
        metadata_label.setStyleSheet("color: #666; font-size: 12px;")
        
        tab_container = self._create_tab_buttons()

        layout.addWidget(campaign_name)
        layout.addWidget(metadata_label)
        layout.addWidget(tab_container)
        
        return tab_widget
    
    def _create_tab_buttons(self) -> QWidget:
        """Create the interactive tab buttons."""
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 10, 0, 0)
        tab_layout.setSpacing(0)
        
        self.tabs["Runs"] = self._create_tab_button("Runs")
        self.tabs["Parameters"] = self._create_tab_button("Parameters")
        self.tabs["Settings"] = self._create_tab_button("Settings")
        
        for name, button in self.tabs.items():
            button.clicked.connect(lambda checked, n=name: self.switch_tab(n))
            tab_layout.addWidget(button)
            
        tab_layout.addStretch()
        return tab_container

    def _create_tab_button(self, text: str) -> QPushButton:
        """Helper to create a single tab button."""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setFixedHeight(40)
        button.setFixedWidth(120)
        button.setFlat(True)
        return button

    def _create_panels(self):
        """Create panels and connect their signals."""
        self.runs_panel = RunsPanel()
        self.parameters_panel = ParametersPanel()
        self.settings_panel = SettingsPanel()

        self.runs_panel.new_run_requested.connect(self.new_run_requested.emit)

        self.stacked_widget.addWidget(self.runs_panel)
        self.stacked_widget.addWidget(self.parameters_panel)
        self.stacked_widget.addWidget(self.settings_panel)
        
        self.switch_tab("Runs")

    def switch_tab(self, name: str):
        """Switch the visible tab and update button styles."""
        for tab_name, button in self.tabs.items():
            is_active = (tab_name == name)
            button.setChecked(is_active)
            button.setObjectName("ActiveTab" if is_active else "InactiveTab")
        
        self.stacked_widget.setCurrentWidget(self.panels[name])
        self.style().polish(self)

    def _create_home_button_section(self) -> QWidget:
        """Create the bottom buttons section."""
        buttons_widget = QWidget()
        layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addStretch()
        
        home_button = SecondaryButton("Home")
        home_button.clicked.connect(self.home_requested.emit)
        layout.addWidget(home_button)
        
        return buttons_widget