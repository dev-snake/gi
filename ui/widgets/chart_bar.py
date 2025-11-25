from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class BarChart(QWidget):
    def __init__(self):
        super().__init__()

        self.fig = Figure(figsize=(4, 3))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, labels, values):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        ax.bar(labels, values, color="#4DB6AC")
        ax.set_ylabel("Milliseconds")
        ax.set_title("Performance Timings")

        self.canvas.draw()

    # so sánh 2 URL
    def plot_compare(self, labels, v1, v2):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        x = range(len(labels))

        ax.bar([i - 0.2 for i in x], v1, width=0.4, label="URL 1", color="#4FC3F7")
        ax.bar([i + 0.2 for i in x], v2, width=0.4, label="URL 2", color="#FFB74D")

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        self.canvas.draw()
