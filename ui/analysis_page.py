from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QFrame,
)
from PyQt6.QtCore import Qt
from core.analyzer import analyze


class AnalysisPage(QWidget):
    """
    Trang phân tích hiệu năng tự động.
    Nhận data từ DashboardPage thông qua hàm set_data().
    """

    def __init__(self):
        super().__init__()

        self.data = None

        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        title = QLabel("Automatic Performance Analysis")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main.addWidget(title)

        # ---------------------------------------------------------
        # 2 LIST: ISSUES + SUGGESTIONS
        # ---------------------------------------------------------
        content = QHBoxLayout()
        content.setSpacing(20)

        # Issues (left)
        left = QVBoxLayout()
        left.setSpacing(10)
        lbl1 = QLabel("⚠️ Issues (Vấn đề phát hiện):")
        lbl1.setStyleSheet("font-size: 16px; font-weight: bold;")
        left.addWidget(lbl1)

        self.issue_list = QListWidget()
        self.issue_list.setMinimumWidth(300)
        left.addWidget(self.issue_list)

        content.addLayout(left, 1)

        # Suggestions (right)
        right = QVBoxLayout()
        right.setSpacing(10)
        lbl2 = QLabel("💡 Suggestions (Gợi ý tối ưu):")
        lbl2.setStyleSheet("font-size: 16px; font-weight: bold;")
        right.addWidget(lbl2)

        self.sug_list = QListWidget()
        self.sug_list.setMinimumWidth(300)
        right.addWidget(self.sug_list)

        content.addLayout(right, 1)

        main.addLayout(content)

    # ===================================================================
    # PUBLIC API: gọi từ dashboard khi user scan xong
    # ===================================================================
    def set_data(self, scan_data: dict):
        self.data = scan_data

        self.issue_list.clear()
        self.sug_list.clear()

        result = analyze(scan_data)

        for issue in result["issues"]:
            self.issue_list.addItem(issue)

        for sug in result["suggestions"]:
            self.sug_list.addItem(sug)
