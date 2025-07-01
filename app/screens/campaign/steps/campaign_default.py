"""
Default screen for campaign when no runs have been created yet.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont, QPixmap, QPainter

from app.core.base import BaseScreen
from app.models.campaign import Campaign
from app.shared.components.buttons import PrimaryButton, SecondaryButton
from app.shared.components.cards import EmptyStateCard


class CampaignDefaultScreen(BaseScreen):
    """
    Default screen for campaign when no runs have been created yet.
    Displays campaign info, tabs, and empty state with call-to-action buttons.
    """

    # Signals
    home_requested = Signal()
    new_run_requested = Signal()

    def __init__(self, wizard_data: Campaign, parent=None):
        super().__init__(wizard_data, parent)
        self.campaign: Campaign = self.wizard_data

    def _setup_screen(self):
        """Setup the default campaign screen UI."""
        main_layout = self._create_main_layout()
        
        # Campaign header section
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # Tab navigation section
        tab_widget = self._create_tab_section()
        main_layout.addWidget(tab_widget)
        
        # Empty state content
        content_widget = self._create_content_section()
        main_layout.addWidget(content_widget)
        
        # Bottom buttons
        buttons_widget = self._create_buttons_section()
        main_layout.addWidget(buttons_widget)

    def _create_main_layout(self) -> QVBoxLayout:
        """Create and configure the main layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

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
        target_info = f"Target(s): {self.campaign.target_parameter.name if self.campaign.target_parameter else 'Undefined Target'}"
        metadata_text = f"Created on 25 April, 2025 • {param_count} Parameters • {target_info}"
        
        metadata_label = QLabel(metadata_text)
        metadata_label.setObjectName("CampaignMetadata")
        metadata_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # Tab buttons
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 10, 0, 0)
        tab_layout.setSpacing(0)
        
        runs_tab = self._create_tab_button("Runs", active=True)
        parameters_tab = self._create_tab_button("Parameters", active=False)
        settings_tab = self._create_tab_button("Settings", active=False)
        
        tab_layout.addWidget(runs_tab)
        tab_layout.addWidget(parameters_tab)
        tab_layout.addWidget(settings_tab)
        tab_layout.addStretch()
        
        layout.addWidget(campaign_name)
        layout.addWidget(metadata_label)
        layout.addWidget(tab_container)
        
        return tab_widget

    def _create_tab_button(self, text: str, active: bool = False) -> QPushButton:
        """Create a tab button."""
        button = QPushButton(text)
        button.setObjectName("ActiveTab" if active else "InactiveTab")
        button.setFixedHeight(40)
        button.setFixedWidth(120)
        button.setFlat(True)
        
        if active:
            button.setStyleSheet("""
                QPushButton#ActiveTab {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton#InactiveTab {
                    background-color: #F0F0F0;
                    color: #666;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton#InactiveTab:hover {
                    background-color: #E0E0E0;
                }
            """)
        
        return button
    
    def _create_empty_state(self):
        icon_pixmap = self._get_clock_icon_pixmap()
        empty_state = EmptyStateCard(
            primary_message="No runs yet",
            secondary_message="Generate your first run to start experimenting",
            icon_pixmap=icon_pixmap,
        )
        self.main_layout.addWidget(empty_state)


    def _create_buttons_section(self) -> QWidget:
        """Create the bottom buttons section."""
        buttons_widget = QWidget()
        layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(20, 0, 20, 40)
        layout.setSpacing(15)
        
        # Add horizontal spacer to right-align buttons
        layout.addStretch()
        
        # Home button (secondary)
        home_button = SecondaryButton("Home")
        home_button.setFixedHeight(40)
        home_button.setFixedWidth(100)
        home_button.clicked.connect(self.home_requested.emit)
        
        # Generate New Run button (primary)
        generate_button = PrimaryButton("Generate New Run")
        generate_button.setFixedHeight(40)
        generate_button.setFixedWidth(160)
        generate_button.clicked.connect(self.new_run_requested.emit)
        
        layout.addWidget(home_button)
        layout.addWidget(generate_button)
        
        return buttons_widget