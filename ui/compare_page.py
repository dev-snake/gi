from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from core.scanner import scan
from ui.widgets.chart_bar import BarChart
from ui.widgets.chart_radar import RadarChart


class ComparePage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("ComparePage")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------
        title = QLabel("Compare Two Websites")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main.addWidget(title)

        # ---------------------------------------------------------
        # INPUT URLs
        # ---------------------------------------------------------
        row = QHBoxLayout()

        self.url1 = QLineEdit()
        self.url1.setPlaceholderText("https://site1.com")
        self.url1.setMinimumHeight(40)

        self.url2 = QLineEdit()
        self.url2.setPlaceholderText("https://site2.com")
        self.url2.setMinimumHeight(40)

        self.btn_compare = QPushButton("Compare")
        self.btn_compare.setMinimumHeight(40)
        self.btn_compare.clicked.connect(self.do_compare)

        row.addWidget(self.url1)
        row.addWidget(self.url2)
        row.addWidget(self.btn_compare)

        main.addLayout(row)

        # ---------------------------------------------------------
        # BAR CHART COMPARISON
        # ---------------------------------------------------------
        self.bar_chart = BarChart()
        main.addWidget(self.bar_chart, stretch=1)

        # ---------------------------------------------------------
        # RADAR CHART
        # ---------------------------------------------------------
        self.radar_chart = RadarChart()
        main.addWidget(self.radar_chart, stretch=1)

        # ---------------------------------------------------------
        # TABLE DIFFERENCE
        # ---------------------------------------------------------
        lbl = QLabel("Comparison Table")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        main.addWidget(lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Metric", "URL 1", "URL 2", "Difference"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        main.addWidget(self.table)

        # ---------------------------------------------------------
        # SUMMARY TEXT
        # ---------------------------------------------------------
        self.lbl_summary = QLabel("")
        self.lbl_summary.setStyleSheet("font-size: 16px;")
        main.addWidget(self.lbl_summary)

        # STATE
        self.data1 = None
        self.data2 = None

    # ====================================================================
    # COMPARE ACTION
    # ====================================================================
    def do_compare(self):
        u1 = self.url1.text().strip()
        u2 = self.url2.text().strip()

        if not u1 or not u2:
            QMessageBox.warning(self, "Error", "Cần nhập đủ 2 URL.")
            return

        try:
            self.data1 = scan(u1)
            self.data2 = scan(u2)

            self.update_charts()
            self.update_table()
            self.update_summary()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ====================================================================
    # UPDATE BAR + RADAR CHARTS
    # ====================================================================
    def update_charts(self):
        m1 = self.data1["metrics"]
        m2 = self.data2["metrics"]

        # BAR CHART
        labels = ["DNS", "TCP", "TTFB", "DOM", "Load"]
        v1 = [m1["dns"], m1["tcp"], m1["ttfb"], m1["dom"], m1["load"]]
        v2 = [m2["dns"], m2["tcp"], m2["ttfb"], m2["dom"], m2["load"]]

        self.bar_chart.plot_compare(labels, v1, v2)

        # RADAR
        vA = [
            max(0, 3000 - m1["ttfb"]) / 3000 * 100,
            max(0, 3000 - m1["dom"]) / 3000 * 100,
            max(0, 3000 - m1["load"]) / 3000 * 100,
            max(0, 2500 - self.data1["vitals"]["LCP"]) / 2500 * 100,
            max(0, 0.1 - self.data1["vitals"]["CLS"]) / 0.1 * 100,
        ]
        vB = [
            max(0, 3000 - m2["ttfb"]) / 3000 * 100,
            max(0, 3000 - m2["dom"]) / 3000 * 100,
            max(0, 3000 - m2["load"]) / 3000 * 100,
            max(0, 2500 - self.data2["vitals"]["LCP"]) / 2500 * 100,
            max(0, 0.1 - self.data2["vitals"]["CLS"]) / 0.1 * 100,
        ]

        self.radar_chart.plot_compare(["TTFB", "DOM", "LOAD", "LCP", "CLS"], vA, vB)

    # ====================================================================
    # UPDATE COMPARISON TABLE
    # ====================================================================
    def update_table(self):
        self.table.setRowCount(0)

        def add_row(name, a, b):
            row = self.table.rowCount()
            self.table.insertRow(row)

            diff = b - a
            diff_str = f"{diff:+}"

            vals = [name, str(a), str(b), diff_str]

            for col, val in enumerate(vals):
                self.table.setItem(row, col, QTableWidgetItem(val))

        m1 = self.data1["metrics"]
        m2 = self.data2["metrics"]

        add_row("DNS", m1["dns"], m2["dns"])
        add_row("TCP", m1["tcp"], m2["tcp"])
        add_row("TTFB", m1["ttfb"], m2["ttfb"])
        add_row("DOM", m1["dom"], m2["dom"])
        add_row("Load", m1["load"], m2["load"])

        # WebVitals
        v1 = self.data1["vitals"]
        v2 = self.data2["vitals"]

        add_row("LCP", int(v1["LCP"]), int(v2["LCP"]))
        add_row("FID", int(v1["FID"]), int(v2["FID"]))
        add_row("CLS", v1["CLS"], v2["CLS"])

        # Size / Request
        add_row(
            "Total Requests", self.data1["total_requests"], self.data2["total_requests"]
        )
        add_row(
            "Total Size (KB)",
            round(self.data1["total_size"] / 1024, 2),
            round(self.data2["total_size"] / 1024, 2),
        )

    # ====================================================================
    # SUMMARY TEXT
    # ====================================================================
    def update_summary(self):
        m1 = self.data1["metrics"]
        m2 = self.data2["metrics"]

        score1 = m1["ttfb"] + m1["dom"] + m1["load"]
        score2 = m2["ttfb"] + m2["dom"] + m2["load"]

        if score1 < score2:
            msg = f"✅ **{self.url1.text()} nhanh hơn tổng thể**"
        elif score2 < score1:
            msg = f"✅ **{self.url2.text()} nhanh hơn tổng thể**"
        else:
            msg = "⚖️ Hai trang có tốc độ tương đương."

        self.lbl_summary.setText(msg)
