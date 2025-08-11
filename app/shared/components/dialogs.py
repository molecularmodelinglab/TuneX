from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

from app.shared.components.buttons import PrimaryButton, DangerButton
from app.shared.styles.theme import get_info_dialog_styles, get_confirmation_dialog_styles, get_error_dialog_styles


class ConfirmationDialog(QDialog):
    """Custom confirmation dialog that follows app styling."""
    
    def __init__(self, title: str, message: str, confirm_text: str = "Yes", 
                 cancel_text: str = "No", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(450, 300)
        
        self._setup_ui(title, message, confirm_text, cancel_text)
        
        self.setObjectName("ConfirmationDialog")
        self.setStyleSheet(get_confirmation_dialog_styles())
           
    def _setup_ui(self, title: str, message: str, confirm_text: str, cancel_text: str):
        """Setup the dialog UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        separator = QFrame()
        separator.setObjectName("DialogSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(message_label)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = PrimaryButton(cancel_text)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.confirm_button = DangerButton(confirm_text)
        self.confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)

    @staticmethod
    def show_confirmation(title: str, message: str, confirm_text: str = "Yes", 
                         cancel_text: str = "No", parent=None) -> bool:
        """Show a confirmation dialog and return True if confirmed."""
        dialog = ConfirmationDialog(title, message, confirm_text, cancel_text, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted


class InfoDialog(QDialog):
    """Custom information dialog that follows app styling."""
    
    def __init__(self, title: str, message: str, button_text: str = "OK", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self._setup_ui(title, message, button_text)
        
        # Apply styling
        self.setObjectName("InfoDialog")
        self.setStyleSheet(get_info_dialog_styles())
            
    def _setup_ui(self, title: str, message: str, button_text: str):
        """Setup the dialog UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setObjectName("DialogSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Message
        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        layout.addStretch()

        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = PrimaryButton(button_text)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    @staticmethod
    def show_info(title: str, message: str, button_text: str = "OK", parent=None):
        """Show an information dialog."""
        dialog = InfoDialog(title, message, button_text, parent)
        dialog.exec()


class ErrorDialog(InfoDialog):
    """Custom error dialog that follows app styling."""
    
    def __init__(self, title: str, message: str, button_text: str = "OK", parent=None):
        super().__init__(title, message, button_text, parent)
        
        # Override styling for error dialog
        self.setStyleSheet(get_error_dialog_styles())

    @staticmethod
    def show_error(title: str, message: str, button_text: str = "OK", parent=None):
        """Show an error dialog."""
        dialog = ErrorDialog(title, message, button_text, parent)
        dialog.exec()