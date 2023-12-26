import sys

from PyQt6.QtWidgets import QApplication

from .ui_elements.image_config_app import ImageExifEditor

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWin = ImageExifEditor()
    mainWin.show()

    sys.exit(app.exec())
