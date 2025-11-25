from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.batch import batch_scan


# ========================================================================
# WORKER THREAD (quét không khóa UI)
# ========================================================================
class BatchWorker(QThread):
    # Use object so we can emit None while a scan is in progress
    progress_signal = pyqtSignal(int, str, str, object)
    finish_signal = pyqtSignal(list)

    def __init__(self, urls: list):
        super().__init__()
        self.urls = urls

    def run(self):
        results = batch_scan(
            self.urls,
            callback_progress=lambda idx, url, status, data: self.progress_signal.emit(
                idx, url, status, data
            ),
        )
        self.finish_signal.emit(results)


# ========================================================================
# BATCH PAGE UI
# ========================================================================
class BatchPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("BatchPage")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # ------------------------------------------------------------
        # TITLE
        # ------------------------------------------------------------
        title = QLabel("Batch Website Scanner")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main.addWidget(title)

        # ------------------------------------------------------------
        # URL INPUT (MULTI-LINE)
        # ------------------------------------------------------------
        input_box = QVBoxLayout()
        input_box.addWidget(QLabel("Nhập danh sách URL (mỗi dòng 1 URL):"))

        self.url_list_box = QTextEdit()
        self.url_list_box.setPlaceholderText(
            "https://site1.com\nhttps://site2.com\nhttps://site3.com"
        )
        self.url_list_box.setMinimumHeight(120)
        input_box.addWidget(self.url_list_box)

        self.btn_start = QPushButton("Start Batch Scan")
        self.btn_start.setMinimumHeight(40)
        self.btn_start.clicked.connect(self.start_batch)
        input_box.addWidget(self.btn_start)

        main.addLayout(input_box)

        # ------------------------------------------------------------
        # TABLE RESULT
        # ------------------------------------------------------------
        lbl_res = QLabel("Results")
        lbl_res.setStyleSheet("font-size: 16px; font-weight: bold;")
        main.addWidget(lbl_res)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "URL",
                "Status",
                "TTFB (ms)",
                "Load (ms)",
                "LCP (ms)",
                "Requests",
                "Size (KB)",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        main.addWidget(self.table)

        # ------------------------------------------------------------
        # SUMMARY / BEST SITE BOX
        # ------------------------------------------------------------
        self.lbl_best = QLabel("")
        self.lbl_best.setStyleSheet("font-size: 15px; font-weight: bold;")
        main.addWidget(self.lbl_best)

        # STATE
        self.results = []

    # ====================================================================
    # START BATCH
    # ====================================================================
    def start_batch(self):
        raw = self.url_list_box.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Error", "Chưa nhập URL.")
            return

        urls = [x.strip() for x in raw.split("\n") if x.strip()]

        if len(urls) == 0:
            QMessageBox.warning(self, "Error", "Danh sách URL rỗng.")
            return

        # Reset table
        self.table.setRowCount(len(urls))
        for i, url in enumerate(urls):
            self.table.setItem(i, 0, QTableWidgetItem(url))
            self.table.setItem(i, 1, QTableWidgetItem("Waiting..."))

        # Run worker
        self.worker = BatchWorker(urls)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finish_signal.connect(self.finish_batch)
        self.worker.start()

    # ====================================================================
    # PROGRESS UPDATE
    # ====================================================================
    def update_progress(self, idx, url, status, data):
        self.table.setItem(idx, 1, QTableWidgetItem(status))

        if data:
            self.table.setItem(idx, 2, QTableWidgetItem(str(data["metrics"]["ttfb"])))
            self.table.setItem(idx, 3, QTableWidgetItem(str(data["metrics"]["load"])))
            self.table.setItem(
                idx, 4, QTableWidgetItem(str(int(data["vitals"]["LCP"])))
            )
            self.table.setItem(idx, 5, QTableWidgetItem(str(data["total_requests"])))
            self.table.setItem(
                idx, 6, QTableWidgetItem(f"{data['total_size']/1024:.2f}")
            )

        self.table.viewport().update()

    # ====================================================================
    # FINISH BATCH
    # ====================================================================
    def finish_batch(self, results):
        # Save all results
        self.results = results

        # Find fastest
        fastest = None
        fastest_score = None

        for url, data in results:
            if data is None:
                continue

            # Lower score = faster
            score = data["metrics"]["ttfb"] + data["metrics"]["load"]

            if fastest is None or score < fastest_score:
                fastest = url
                fastest_score = score

        if fastest:
            self.lbl_best.setText(f"🏆 Trang nhanh nhất: **{fastest}**")
        else:
            self.lbl_best.setText("❗ Không có trang nào scan thành công.")
