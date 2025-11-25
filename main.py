import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
from ui.main_window import MainWindow
from core.database import init_db

if __name__ == "__main__":
    # Initialize database
    init_db()

    app = QApplication(sys.argv)

    # Load global QSS
    qss = QFile("assets/style.qss")
    if qss.exists():
        if qss.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(qss)
            app.setStyleSheet(stream.readAll())
            qss.close()

    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())
