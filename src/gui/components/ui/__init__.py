# src/component/ui/__init__.py
from .audio_controls import AudioControls

# ui/components.py (optional, for other UI components)
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class CustomComponent(QWidget):
    """Template for other UI components"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)