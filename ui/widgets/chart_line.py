from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class LineChart(QWidget):
    def __init__(self):
        super().__init__()

        self.fig = Figure(figsize=(4, 3))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, values):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        ax.plot(values, marker="o", linestyle="-", color="#9575CD")
        ax.set_title("Timeline")
        ax.set_ylabel("Duration (ms)")
        ax.set_xlabel("Request Index")

        self.canvas.draw()
