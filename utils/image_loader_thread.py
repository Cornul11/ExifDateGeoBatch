from PyQt6.QtCore import QDir, QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QStandardItem


class ImageLoaderThread(QThread):
    progress_update = pyqtSignal(int)
    finished_loading = pyqtSignal(list)

    def __init__(self, folder_path, max_thumbnail_size):
        super().__init__()
        self.folder_path = folder_path
        self.thumbnail_size = QSize(max_thumbnail_size, max_thumbnail_size)

    def run(self):
        img_dir = QDir(self.folder_path)
        file_list = img_dir.entryList(["*.jpg", "*.png", "*.bmp"])
        total_files = len(file_list)
        loaded_images = []

        for i, file in enumerate(file_list):
            pixmap = QPixmap(img_dir.absoluteFilePath(file)).scaled(
                self.thumbnail_size, Qt.AspectRatioMode.KeepAspectRatio
            )
            icon = QIcon(pixmap)

            item = QStandardItem(icon, file)
            loaded_images.append(item)

            progress = int((i + 1) / total_files * 100)
            self.progress_update.emit(progress)

        self.finished_loading.emit(loaded_images)
