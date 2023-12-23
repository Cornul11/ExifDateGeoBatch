from PyQt6.QtCore import QObject, pyqtSlot


class PythonBridge(QObject):
    def __init__(self, window):
        super().__init__()
        self.main_window = window

    @pyqtSlot(float, float)
    def coordinatesChanged(self, lat, lng):
        if self.main_window:
            self.main_window.set_coordinates(lat, lng)
