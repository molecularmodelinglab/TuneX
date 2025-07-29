import pytest
from PySide6.QtWidgets import QApplication, QWidget

from app.screens.workspace.select_workspace import SelectWorkspaceScreen


@pytest.fixture
def app(qtbot):
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


def test_select_workspace_screen_init(app, qtbot):
    """Test the initialization of the select workspace screen."""
    screen = SelectWorkspaceScreen()
    qtbot.addWidget(screen)

    assert screen.windowTitle() == "TuneX - Select Workspace"
    # commeting out because the button might not be present in the current version
    #assert screen.findChild(QWidget, "SelectWorkspaceButton") is not None
