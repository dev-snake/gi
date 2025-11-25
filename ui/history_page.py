from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from core.database import get_history, get_scan, delete_history, clear_history


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("HistoryPage")

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # ------------------------------------------------------------
        # TITLE
        # ------------------------------------------------------------
        title = QLabel("Scan History")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main.addWidget(title)

        # ------------------------------------------------------------
        # TABLE
        # ------------------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "URL", "TTFB", "Load", "LCP", "Requests", "Size (KB)", "Time"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.ExtendedSelection)
        self.table.cellDoubleClicked.connect(self.view_detail)

        main.addWidget(self.table)

        # ------------------------------------------------------------
        # BUTTONS (DELETE / REFRESH)
        # ------------------------------------------------------------
        btns = QHBoxLayout()

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_history)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.delete_selected)

        self.btn_compare = QPushButton("Compare Selected")
        self.btn_compare.clicked.connect(self.compare_selected)

        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.clicked.connect(self.clear_all)

        btns.addWidget(self.btn_refresh)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_compare)
        btns.addWidget(self.btn_clear)
        btns.addStretch()

        main.addLayout(btns)

        # Load immediately
        self.load_history()

        # hold selected data
        self.current_selected_data = None

    # ====================================================================
    # LOAD HISTORY INTO TABLE
    # ====================================================================
    def load_history(self):
        rows = get_history()
        self.table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                # Size: convert to KB
                if col_idx == 6:
                    val = f"{val / 1024:.1f}"
                item = QTableWidgetItem(str(val))
                self.table.setItem(row_idx, col_idx, item)

    # ====================================================================
    # VIEW DETAILS (DOUBLE CLICK)
    # ====================================================================
    def view_detail(self, row, col):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        id_val = int(id_item.text())

        data = get_scan(id_val)
        if not data:
            QMessageBox.warning(self, "Error", "Không tải được dữ liệu.")
            return

        # Save for external usage (Dashboard / Resources / Analysis)
        self.current_selected_data = data

        # Popup summary
        msg = (
            f"URL: {data['url']}\n"
            f"TTFB: {data['metrics']['ttfb']} ms\n"
            f"Load: {data['metrics']['load']} ms\n"
            f"LCP: {int(data['vitals']['LCP'])} ms\n"
            f"Requests: {data['total_requests']}\n"
            f"Size: {data['total_size']/1024:.2f} KB\n"
        )
        QMessageBox.information(self, "Scan Details", msg)

    # ====================================================================
    # DELETE SELECTED
    # ====================================================================
    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Chưa chọn dòng nào.")
            return

        id_val = int(self.table.item(row, 0).text())

        delete_history(id_val)
        self.load_history()
        QMessageBox.information(self, "Done", "Đã xóa.")

    # ====================================================================
    # CLEAR ALL
    # ====================================================================
    def clear_all(self):
        if (
            QMessageBox.question(
                self, "Confirm", "Xóa toàn bộ lịch sử?"
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        clear_history()
        self.load_history()
        QMessageBox.information(self, "Done", "Đã xóa toàn bộ.")

    # ====================================================================
    # COMPARE TWO SCANS (BEFORE / AFTER)
    # ====================================================================
    def compare_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 2:
            QMessageBox.warning(self, "Error", "Chon chinh xac 2 dong de so sanh (Before/After).")
            return

        ids = []
        for idx in selected_rows:
            id_item = self.table.item(idx.row(), 0)
            if id_item:
                ids.append(int(id_item.text()))

        if len(ids) != 2:
            QMessageBox.warning(self, "Error", "Khong doc duoc ID cua 2 dong.")
            return

        before_id, after_id = sorted(ids)
        before = get_scan(before_id)
        after = get_scan(after_id)

        if not before or not after:
            QMessageBox.warning(self, "Error", "Khong lay duoc du lieu scan.")
            return

        def fmt(name, b_val, a_val, lower_is_better=True):
            delta = a_val - b_val
            pct_str = "n/a" if b_val == 0 else f"{(delta / b_val) * 100:+.1f}%"
            direction = "down" if (lower_is_better and delta < 0) or (not lower_is_better and delta > 0) else "up"
            return f"{name}: Before {b_val}, After {a_val} ({delta:+}, {pct_str}) {direction}"

        lines = [
            fmt("TTFB (ms)", before["metrics"]["ttfb"], after["metrics"]["ttfb"]),
            fmt("Load (ms)", before["metrics"]["load"], after["metrics"]["load"]),
            fmt("LCP (ms)", int(before["vitals"]["LCP"]), int(after["vitals"]["LCP"])),
            fmt("CLS", before["vitals"]["CLS"], after["vitals"]["CLS"], lower_is_better=True),
            fmt("Requests", before["total_requests"], after["total_requests"]),
            fmt(
                "Total Size (KB)",
                round(before["total_size"] / 1024, 2),
                round(after["total_size"] / 1024, 2),
            ),
        ]

        score_before = before["metrics"]["ttfb"] + before["metrics"]["load"]
        score_after = after["metrics"]["ttfb"] + after["metrics"]["load"]
        headline = "Nhanh hon sau toi uu!" if score_after < score_before else "Can toi uu them."

        msg = headline + "\n\n" + "\n".join(lines)
        QMessageBox.information(self, "Before / After", msg)
