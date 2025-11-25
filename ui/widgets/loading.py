from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer


class LoadingSpinner(QWidget):
    def __init__(self, text="Loading..."):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(text)
        self.label.setStyleSheet("font-size: 14px; color: white;")

        self.dot_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(300)

        layout.addWidget(self.label)

    def update_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.label.setText("Loading" + "." * self.dot_count)
