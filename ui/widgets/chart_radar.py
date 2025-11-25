from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


class RadarChart(QWidget):
    def __init__(self):
        super().__init__()

        self.fig = Figure(figsize=(4, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, labels, values):
        self.fig.clear()
        ax = self._radar(labels, values)
        self.canvas.draw()

    def plot_compare(self, labels, v1, v2):
        self.fig.clear()

        N = len(labels)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]

        v1 = v1 + v1[:1]
        v2 = v2 + v2[:1]

        ax = self.fig.add_subplot(111, polar=True)

        ax.plot(angles, v1, label="URL 1", color="#4FC3F7")
        ax.fill(angles, v1, alpha=0.25, color="#4FC3F7")

        ax.plot(angles, v2, label="URL 2", color="#FF8A65")
        ax.fill(angles, v2, alpha=0.25, color="#FF8A65")

        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.legend()

        self.canvas.draw()

    def _radar(self, labels, values):
        N = len(labels)

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values = values + values[:1]
        angles += angles[:1]

        ax = self.fig.add_subplot(111, polar=True)
        ax.plot(angles, values, color="#4DB6AC")
        ax.fill(angles, values, alpha=0.3, color="#4DB6AC")
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        return ax
