import sys

from PyQt5.QtCore import QDir, QSize
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, \
    QDesktopWidget, QAbstractItemView, QListView, QGridLayout


class ImageConfigApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(QSize(800, 600))

        self.setWindowTitle("Exif GUI editor")

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout: horizontal
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left pane: image list
        self.image_list_widget = QListView()
        self.image_list_widget.setViewMode(QListView.IconMode)
        self.image_list_widget.setIconSize(QSize(150, 150))
        self.image_list_widget.setGridSize(QSize(160, 180))
        self.image_list_widget.setSpacing(10)
        self.image_list_widget.setFlow(QListView.LeftToRight)
        self.image_list_widget.setResizeMode(QListView.Adjust)

        self.image_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.image_list_widget.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.grid_layout = QGridLayout(self.image_list_widget)
        self.main_layout.addWidget(self.image_list_widget)

        # Right pane: configs
        self.config_layout = QVBoxLayout()
        self.config_label = QLabel("Configurations here")
        self.config_layout.addWidget(self.config_label)
        self.main_layout.addLayout(self.config_layout)

        self.load_images_from_folder("/home/dan/Pictures/")

        self.center_window()

    def handle_empty_space_click(self, item):
        print(self.image_list_widget.selectedIndexes())
        if not self.image_list_widget.selectedIndexes():
            self.image_list_widget.clearSelection()

    def center_window(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))

    def load_images_from_folder(self, folder_path):
        img_dir = QDir(folder_path)

        file_list = img_dir.entryList()

        model = QStandardItemModel()

        for file in file_list:
            # check if an image
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                continue

            pixmap = QPixmap(img_dir.absoluteFilePath(file))
            icon = QIcon(pixmap)

            item = QStandardItem(icon, file)
            item.setSelectable(True)
            model.appendRow(item)

        self.image_list_widget.setModel(model)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWin = ImageConfigApp()
    mainWin.show()

    sys.exit(app.exec_())
