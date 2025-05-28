from PySide6.QtWidgets import QWidget


class ParametersStep(QWidget):
    def __init__(self, campaign_data):
        super().__init__()
        self.campaign_data = campaign_data

    def validate(self):
        return True

    def save_data(self):
        pass

    def load_data(self):
        pass
