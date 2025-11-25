from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


class Heatmap(QWidget):
    def __init__(self):
        super().__init__()

        self.fig = Figure(figsize=(4, 3))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def set_data(self, values):
        if not values:
            return

        arr = np.array(values).reshape(1, -1)

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        heat = ax.imshow(arr, cmap="inferno", aspect="auto")
        ax.set_yticks([])
        ax.set_title("Resource Duration Heatmap")
        self.canvas.draw()
