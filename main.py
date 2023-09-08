import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow


class HelloWorldWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello World!")

        label = QLabel("Hello World!", self)
        self.setCentralWidget(label)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWin = HelloWorldWindow()
    mainWin.show()
    sys.exit(app.exec_())
