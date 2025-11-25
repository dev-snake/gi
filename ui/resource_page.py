from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from ui.widgets.heatmap import Heatmap
from ui.widgets.chart_bar import BarChart


class ResourcePage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("ResourcePage")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # STATE
        self.data = None

        # ---------------------------------------------------------
        # HEADER: Title + Filter
        # ---------------------------------------------------------
        header = QHBoxLayout()

        title = QLabel("Resource Timing")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        header.addWidget(title)
        header.addStretch()

        # Filter by initiatorType
        self.filter_box = QComboBox()
        self.filter_box.addItems([
            "all",
            "img",
            "script",
            "css",
            "font",
            "xhr",
            "fetch",
            "iframe",
            "other",
        ])
        self.filter_box.currentTextChanged.connect(self.apply_filter)

        header.addWidget(QLabel("Filter:"))
        header.addWidget(self.filter_box)

        main.addLayout(header)

        # ---------------------------------------------------------
        # TABLE: Resource List
        # ---------------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Type",
            "Duration (ms)",
            "Size (KB)",
            "Start Time (ms)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main.addWidget(self.table)

        # ---------------------------------------------------------
        # SECTION: Breakdown + Slowest + Heatmap
        # ---------------------------------------------------------
        section = QHBoxLayout()

        # Breakdown (bar chart)
        self.breakdown_chart = BarChart()
        section.addWidget(self.breakdown_chart, 2)

        # Heatmap
        self.heatmap = Heatmap()
        section.addWidget(self.heatmap, 2)

        main.addLayout(section)

        # Slowest list
        slow_box = QVBoxLayout()
        slow_box.addWidget(QLabel("Top 10 Slowest Resources:"))

        self.slowest_table = QTableWidget()
        self.slowest_table.setColumnCount(4)
        self.slowest_table.setHorizontalHeaderLabels([
            "Name", "Type", "Duration (ms)", "Size (KB)"
        ])
        self.slowest_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        slow_box.addWidget(self.slowest_table)
        main.addLayout(slow_box)


    # ====================================================================
    # PUBLIC: Set data from Dashboard scan
    # ====================================================================
    def set_data(self, data: dict):
        """
        DashboardPage gọi hàm này để truyền data vào ResourcePage
        (khi scan xong)
        """
        self.data = data
        self.apply_filter()       # fill table
        self.update_breakdown()   # bar chart
        self.update_heatmap()     # heatmap
        self.update_slowest()     # slowest list


    # ====================================================================
    # FILTER TABLE
    # ====================================================================
    def apply_filter(self):
        if self.data is None:
            return

        resources = self.data["resources"]
        f = self.filter_box.currentText()

        if f != "all":
            resources = [r for r in resources if r.get("initiatorType") == f]

        self.fill_table(resources)


    def fill_table(self, items):
        self.table.setRowCount(len(items))

        for row, r in enumerate(items):
            name = r.get("name", "")[-60:]   # crop for UI
            typ = r.get("initiatorType", "other")
            dur = round(r.get("duration", 0))
            size = round(r.get("transferSize", 0) / 1024, 2)
            start = round(r.get("startTime", 0))

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(typ))
            self.table.setItem(row, 2, QTableWidgetItem(str(dur)))
            self.table.setItem(row, 3, QTableWidgetItem(str(size)))
            self.table.setItem(row, 4, QTableWidgetItem(str(start)))


    # ====================================================================
    # BREAKDOWN BAR CHART
    # ====================================================================
    def update_breakdown(self):
        if self.data is None:
            return

        breakdown = self.data["breakdown"]
        labels = []
        values = []

        for typ, info in breakdown.items():
            labels.append(typ)
            values.append(info["duration"])

        self.breakdown_chart.plot(labels, values)


    # ====================================================================
    # HEATMAP
    # ====================================================================
    def update_heatmap(self):
        if self.data is None:
            return

        resources = self.data["resources"]

        # Build timeline matrix (simple mapping duration -> color intensity)
        times = [int(r.get("duration", 0)) for r in resources]
        self.heatmap.set_data(times)


    # ====================================================================
    # SLOWEST RESOURCES
    # ====================================================================
    def update_slowest(self):
        if self.data is None:
            return

        slowest = self.data["slowest"]

        self.slowest_table.setRowCount(len(slowest))

        for row, r in enumerate(slowest):
            name = r.get("name", "")[-60:]
            typ = r.get("initiatorType", "other")
            dur = round(r.get("duration", 0))
            size = round(r.get("transferSize", 0) / 1024, 2)

            self.slowest_table.setItem(row, 0, QTableWidgetItem(name))
            self.slowest_table.setItem(row, 1, QTableWidgetItem(typ))
            self.slowest_table.setItem(row, 2, QTableWidgetItem(str(dur)))
            self.slowest_table.setItem(row, 3, QTableWidgetItem(str(size)))
