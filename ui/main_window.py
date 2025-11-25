from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget
from ui.dashboard_page import DashboardPage
from ui.resource_page import ResourcePage
from ui.analysis_page import AnalysisPage
from ui.compare_page import ComparePage
from ui.history_page import HistoryPage
from ui.batch_page import BatchPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WebSpeed Suite")
        self.setMinimumSize(1300, 800)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems(
            ["Dashboard", "Resources", "Analysis", "Compare", "History", "Batch Scan"]
        )
        self.sidebar.setFixedWidth(200)
        self.sidebar.setFocusPolicy(self.sidebar.focusPolicy())
        self.sidebar.currentRowChanged.connect(self.change_page)

        # Add sidebar (NO stretch)
        layout.addWidget(self.sidebar, stretch=0)

        # Pages
        self.pages = {
            0: DashboardPage(),
            1: ResourcePage(),
            2: AnalysisPage(),
            3: ComparePage(),
            4: HistoryPage(),
            5: BatchPage(),
        }

        self.current_page = self.pages[0]

        # Add content page (WITH stretch)
        layout.addWidget(self.current_page, stretch=1)

        self.setCentralWidget(container)

    def change_page(self, index):
        new_page = self.pages[index]

        # nếu có data từ scan dashboard
        if hasattr(self.pages[0], "last_data") and self.pages[0].last_data:
            if hasattr(new_page, "set_data"):
                new_page.set_data(self.pages[0].last_data)

        layout = self.centralWidget().layout()
        layout.replaceWidget(self.current_page, new_page)

        self.current_page.hide()
        new_page.show()

        self.current_page = new_page
