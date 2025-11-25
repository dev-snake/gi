from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from core.scanner import scan
from ui.widgets.chart_bar import BarChart
from ui.widgets.chart_radar import RadarChart
from ui.widgets.card import MetricCard


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("DashboardPage")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # ---------------------------------------------------------
        # INPUT: URL + SCAN BUTTON
        # ---------------------------------------------------------
        input_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setMinimumHeight(40)

        self.btn_scan = QPushButton("Scan")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.clicked.connect(self.do_scan)

        input_row.addWidget(self.url_input)
        input_row.addWidget(self.btn_scan)
        main.addLayout(input_row)

        # ---------------------------------------------------------
        # SUMMARY CARDS (DNS / TCP / TTFB / DOM / LOAD)
        # ---------------------------------------------------------
        card_row = QHBoxLayout()

        self.card_dns = MetricCard("DNS", "0 ms")
        self.card_tcp = MetricCard("TCP", "0 ms")
        self.card_ttfb = MetricCard("TTFB", "0 ms")
        self.card_dom = MetricCard("DOM Load", "0 ms")
        self.card_load = MetricCard("Load", "0 ms")

        card_row.addWidget(self.card_dns)
        card_row.addWidget(self.card_tcp)
        card_row.addWidget(self.card_ttfb)
        card_row.addWidget(self.card_dom)
        card_row.addWidget(self.card_load)

        main.addLayout(card_row)

        # ---------------------------------------------------------
        # WEB VITALS CARDS
        # ---------------------------------------------------------
        vitals_row = QHBoxLayout()

        self.card_lcp = MetricCard("LCP", "0 ms")
        self.card_fid = MetricCard("FID", "0 ms")
        self.card_cls = MetricCard("CLS", "0")

        vitals_row.addWidget(self.card_lcp)
        vitals_row.addWidget(self.card_fid)
        vitals_row.addWidget(self.card_cls)

        main.addLayout(vitals_row)

        # ---------------------------------------------------------
        # CHARTS
        # ---------------------------------------------------------
        chart_row = QHBoxLayout()

        self.chart_bar = BarChart()
        self.chart_radar = RadarChart()

        chart_row.addWidget(self.chart_bar, stretch=1)
        chart_row.addWidget(self.chart_radar, stretch=1)

        main.addLayout(chart_row)

        # ---------------------------------------------------------
        # FOOTER STATS
        # ---------------------------------------------------------
        footer = QHBoxLayout()
        self.lbl_requests = QLabel("Requests: 0")
        self.lbl_size = QLabel("Total Size: 0 KB")

        footer.addWidget(self.lbl_requests)
        footer.addWidget(self.lbl_size)
        footer.addStretch()

        main.addLayout(footer)

        # ---------------------------------------------------------
        # STATE
        # ---------------------------------------------------------
        self.last_data = None


    # ============================================================
    # ACTION: SCAN WEBSITE
    # ============================================================
    def do_scan(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "URL không được để trống.")
            return

        try:
            data = scan(url)
            self.last_data = data
            self.update_ui(data)

        except Exception as e:
            QMessageBox.critical(self, "Scan Failed", str(e))


    # ============================================================
    # UPDATE UI
    # ============================================================
    def update_ui(self, data: dict):
        m = data["metrics"]

        # BASIC CARD METRICS
        self.card_dns.set_value(f"{m['dns']} ms")
        self.card_tcp.set_value(f"{m['tcp']} ms")
        self.card_ttfb.set_value(f"{m['ttfb']} ms")
        self.card_dom.set_value(f"{m['dom']} ms")
        self.card_load.set_value(f"{m['load']} ms")

        # WEB VITALS
        v = data["vitals"]
        self.card_lcp.set_value(f"{int(v['LCP'])} ms")
        self.card_fid.set_value(f"{int(v['FID'])} ms")
        self.card_cls.set_value(str(v['CLS']))

        # CHART BAR
        self.chart_bar.plot(
            ["DNS", "TCP", "TTFB", "DOM", "LOAD"],
            [m["dns"], m["tcp"], m["ttfb"], m["dom"], m["load"]]
        )

        # CHART RADAR
        radar_vals = [
            max(0, 3000 - m["ttfb"]) / 3000 * 100,
            max(0, 3000 - m["dom"]) / 3000 * 100,
            max(0, 3000 - m["load"]) / 3000 * 100,
            max(0, 2500 - v["LCP"]) / 2500 * 100,
            max(0, 0.10 - v["CLS"]) / 0.10 * 100,
        ]

        self.chart_radar.plot(
            ["TTFB", "DOM", "LOAD", "LCP", "CLS"],
            radar_vals
        )

        # FOOTER
        self.lbl_requests.setText(f"Requests: {data['total_requests']}")
        self.lbl_size.setText(f"Total Size: {data['total_size'] / 1024:.2f} KB")
