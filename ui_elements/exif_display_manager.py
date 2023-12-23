from PyQt6.QtWidgets import QLabel


class ExifDisplayManager:
    def __init__(self, parent):
        self.parent = parent
        self.exif_data_label = QLabel("EXIF data will be shown here")
