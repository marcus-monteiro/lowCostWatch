import sys
from PyQt6.QtWidgets import QApplication
from ui.log_viewer_window import LogViewerWindow

def main():
    app = QApplication(sys.argv)
    window = LogViewerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()