from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class MetricCard(QFrame):
    def __init__(self, title: str, value: str):
        super().__init__()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel(title)
        self.title.setStyleSheet("font-size: 14px; opacity: 0.7;")

        self.value = QLabel(value)
        self.value.setStyleSheet("font-size: 22px; font-weight: bold;")

        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_value(self, text: str):
        self.value.setText(text)
