import sys

from PyQt6.QtWidgets import QApplication

from ui_elements.image_config_app import ImageExifEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_win = ImageExifEditor()
    main_win.show()

    sys.exit(app.exec())
