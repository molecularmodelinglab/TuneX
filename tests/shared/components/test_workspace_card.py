"""
Tests for the WorkspaceCard component.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.models.workspace import Workspace
from app.shared.components.workspace_card import WorkspaceCard


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_workspace():
    """Create a sample workspace for testing."""
    workspace = Workspace(
        path="/path/to/workspace", name="Test Workspace", accessed_at=datetime(2023, 1, 15, 10, 30, 0)
    )
    return workspace


@pytest.fixture
def workspace_card(qapp, sample_workspace):
    """Create a WorkspaceCard instance for testing."""
    return WorkspaceCard(sample_workspace)


def test_workspace_card_initialization(workspace_card, sample_workspace):
    """Test that WorkspaceCard is initialized correctly."""
    # Assert
    assert workspace_card.workspace == sample_workspace
    assert workspace_card.objectName() == "WorkspaceCard"
    from PySide6.QtCore import Qt

    assert workspace_card.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_workspace_card_displays_workspace_name(workspace_card, sample_workspace):
    """Test that WorkspaceCard displays the workspace name."""
    # Assert
    assert workspace_card.name_label.text() == sample_workspace.name


def test_workspace_card_displays_workspace_details(workspace_card, sample_workspace):
    """Test that WorkspaceCard displays workspace path details."""
    # Assert
    # Should show "Path: workspace" (basename of the path)
    assert workspace_card.details_label.text() == "Path: workspace"


def test_workspace_card_displays_last_accessed_date(workspace_card, sample_workspace):
    """Test that WorkspaceCard displays the last accessed date."""
    # Assert
    expected_date = "Accessed Jan 15, 2023"
    assert workspace_card.date_label.text() == expected_date


def test_workspace_card_emits_signal_on_click(workspace_card, sample_workspace):
    """Test that WorkspaceCard emits workspace_selected signal when clicked."""
    # Arrange
    mock_slot = MagicMock()
    workspace_card.workspace_selected.connect(mock_slot)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QMouseEvent

    # Act
    # Create a proper mouse event
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        workspace_card.rect().center(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    workspace_card.mousePressEvent(event)

    # Assert
    mock_slot.assert_called_once_with(sample_workspace.path)


def test_workspace_card_with_none_accessed_at():
    """Test that WorkspaceCard handles None accessed_at correctly."""
    # Arrange
    workspace = Workspace(path="/test/path", name="Test Workspace")
    workspace.accessed_at = None

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)

    # Assert
    assert card.date_label.text() == "Never accessed"


def test_workspace_card_with_empty_name():
    """Test that WorkspaceCard handles empty workspace name."""

    # Arrange
    workspace = Workspace(path="/test/path", name="")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)

    # Assert
    # Should auto-generate name from path basename
    assert card.name_label.text() == "path"

    # Should use 'W' as default initial for avatar
    # We can't easily test the pixmap content, but we can verify the card was created
    assert card.icon_label is not None


def test_workspace_card_with_nested_path():
    """Test that WorkspaceCard handles nested paths correctly."""
    # Arrange
    workspace = Workspace(
        path="/home/user/projects/my-awesome-project",
        name="My Awesome Project",
        accessed_at=datetime(2023, 6, 20, 14, 15, 0),
    )

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)

    # Assert
    # Should show only the basename of the path
    assert card.details_label.text() == "Path: my-awesome-project"


def test_workspace_card_with_root_path():
    """Test that WorkspaceCard handles root-level paths correctly."""
    # Arrange
    workspace = Workspace(path="/workspace", name="Root Workspace", accessed_at=datetime(2023, 3, 10, 9, 0, 0))

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)

    # Assert
    assert card.details_label.text() == "Path: workspace"


def test_workspace_card_uses_different_colors():
    """Test that WorkspaceCard uses different color scheme than CampaignCard."""
    # Arrange
    workspace = Workspace(path="/test", name="Test")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)

    # Assert
    # We can't easily test the exact color values, but we can verify the color
    # generation method is called and returns a color
    color = card._get_workspace_color()
    assert color is not None
    assert hasattr(color, "hue")  # QColor should have hue property

    # Verify workspace-specific saturation/value constants are used
    assert card.WORKSPACE_COLOR_SATURATION == 160
    assert card.WORKSPACE_COLOR_VALUE == 200


def test_workspace_card_signal_emits_path_string():
    """Test that WorkspaceCard signal emits path string, not workspace object."""
    # Arrange
    workspace = Workspace(path="/unique/test/path", name="Signal Test")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    card = WorkspaceCard(workspace)
    mock_slot = MagicMock()
    card.workspace_selected.connect(mock_slot)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QMouseEvent

    # Act
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        card.rect().center(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    card.mousePressEvent(event)

    # Assert
    # Should emit the path string, not the workspace object
    mock_slot.assert_called_once_with("/unique/test/path")
    # Verify it's a string, not a Workspace object
    call_args = mock_slot.call_args[0][0]
    assert isinstance(call_args, str)
    assert call_args == workspace.path
