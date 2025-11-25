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

        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.clicked.connect(self.clear_all)

        btns.addWidget(self.btn_refresh)
        btns.addWidget(self.btn_delete)
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
                if col_idx == 5:
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
            QMessageBox.question(self, "Confirm", "Xóa toàn bộ lịch sử?")
            != QMessageBox.Yes
        ):
            return

        clear_history()
        self.load_history()
        QMessageBox.information(self, "Done", "Đã xóa toàn bộ.")
