import os
import re
import sys
from datetime import datetime

import piexif
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, \
    QDesktopWidget, QAbstractItemView, QListView, QLineEdit, QPushButton, QSplitter, QGroupBox, \
    QFormLayout, QStatusBar, QFileDialog, QSlider, QHBoxLayout, QSpacerItem, QSizePolicy, QProgressBar

from custom_list_view import CustomListView
from image_loader import ImageLoaderThread


class ImageConfigApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_directory = ""

        self.resize(QSize(1280, 720))

        self.setWindowTitle("Exif GUI editor")

        splitter = QSplitter(self)
        self.setCentralWidget(splitter)

        # Left pane: image list
        self.image_list_widget = CustomListView()
        self.setup_image_list()

        # Right pane: configs
        config_widget = QWidget()
        self.config_layout = QVBoxLayout(config_widget)

        self.init_batch_edit_widgets()
        self.setup_config_panel()

        splitter.addWidget(self.image_list_widget)
        splitter.addWidget(config_widget)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.hide()
        self.statusBar.addPermanentWidget(self.progress_bar)

        self.thumbnail_size_control = QWidget()
        self.init_thubmnail_size_slider()


        self.center_window()

        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 5px;
                background-color: #efefef;
                border: 1px solid #c0c0c0;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QLineEdit {
                border: 1px solid #c0c0c0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)

    def init_thubmnail_size_slider(self):
        thumbnail_size_layout = QHBoxLayout(self.thumbnail_size_control)
        thumbnail_size_layout.setContentsMargins(0, 0, 0, 0)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        thumbnail_size_layout.addSpacerItem(spacer)
        self.thumbnail_size_slider = QSlider(Qt.Horizontal, self)
        self.thumbnail_size_slider.setMinimum(50)
        self.thumbnail_size_slider.setMaximum(200)
        self.thumbnail_size_slider.setValue(100)
        self.thumbnail_size_slider.valueChanged.connect(self.on_thumbnail_size_changed)
        self.thumbnail_size_slider.setFixedWidth(150)
        thumbnail_size_layout.addWidget(self.thumbnail_size_slider)
        self.statusBar.addPermanentWidget(self.thumbnail_size_control)

    def on_thumbnail_size_changed(self, value):
        self.image_list_widget.setIconSize(QSize(value, value))
        self.image_list_widget.setGridSize(QSize(value + 20, value + 20))

    def init_batch_edit_widgets(self):
        self.directory_btn = QPushButton("Select Directory")
        self.directory_btn.clicked.connect(self.select_directory)
        self.date_edit = QLineEdit()
        self.gps_edit = QLineEdit()
        self.apply_btn = QPushButton("Apply changes")
        self.apply_btn.clicked.connect(self.apply_batch_edit)

    def select_directory(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.current_directory = folder_path
            self.load_images_from_folder(folder_path)
        else:
            self.statusBar.showMessage("No directory selected", 5000)

    def hide_batch_edit_widgets(self):
        self.date_edit.hide()
        self.gps_edit.hide()
        self.apply_btn.hide()

    def prepare_batch_edit(self):
        self.exif_data_label.setText("")
        self.show_batch_edit_widgets()

    def show_batch_edit_widgets(self, single_image=True):
        self.date_edit.show()
        self.gps_edit.show()
        self.apply_btn.show()
        if not single_image:
            self.date_edit.clear()
            self.gps_edit.clear()

    def on_image_selected(self, selected, deselected):
        indexes = self.image_list_widget.selectedIndexes()
        if not indexes:
            self.hide_batch_edit_widgets()
            self.statusBar.showMessage("No images selected", 5000)
            return

        self.display_exif_data(indexes)

    def display_exif_data(self, indexes):
        if len(indexes) == 1:
            filename = indexes[0].data()
            filepath = os.path.join(self.current_directory, filename)
            try:
                exif_dict = piexif.load(filepath)
                self.show_exif_data(exif_dict, filename)
            except Exception as e:
                self.statusBar.showMessage(f"Error processing file {filepath}: {e}", 5000)
                self.exif_data_label.setText(f"{filename}: Error reading EXIF data - {e}")
            self.show_batch_edit_widgets(single_image=True)
        else:
            self.exif_data_label.setText("Multiple images selected.\nApply batch EXIF data changes.")
            self.show_batch_edit_widgets(single_image=False)

    def show_exif_data(self, exif_dict, filename):
        exif_data_texts = [f"File: {filename}"]
        current_date = current_gps = ""

        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            current_date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
            current_date = current_date[:10].replace(':', '-')
            exif_data_texts.append(f"Original Creation Date: {current_date}")

        if 'GPS' in exif_dict:
            gps_data = self.parse_gps_data(exif_dict['GPS'])
            current_gps = f"{gps_data.get('Latitude', '')}, {gps_data.get('Longitude', '')}".strip(', ')
            exif_data_texts.append(f"GPS Coordinates: {current_gps}")

        self.exif_data_label.setText("\n".join(exif_data_texts))
        self.date_edit.setText(current_date)
        self.gps_edit.setText(current_gps)

    def format_gps_display(self, gps_data):
        lat = gps_data.get('Latitude', 'No GPS Latitude Data')
        lon = gps_data.get('Longitude', 'No GPS Longitude Data')

        return f"Latitude: {lat}, Longitude: {lon}"

    def parse_gps_data(self, gps_dict):
        gps_data = {}
        try:
            if piexif.GPSIFD.GPSLatitude in gps_dict and piexif.GPSIFD.GPSLatitudeRef in gps_dict:
                lat = self.convert_to_degrees(gps_dict[piexif.GPSIFD.GPSLatitude])
                lat_ref = gps_dict[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
                lat *= -1 if lat_ref != 'N' else 1
                gps_data['Latitude'] = lat

            if piexif.GPSIFD.GPSLongitude in gps_dict and piexif.GPSIFD.GPSLongitudeRef in gps_dict:
                lon = self.convert_to_degrees(gps_dict[piexif.GPSIFD.GPSLongitude])
                lon_ref = gps_dict[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
                lon *= -1 if lon_ref != 'E' else 1
                gps_data['Longitude'] = lon
        except KeyError as e:
            self.statusBar.showMessage(f"GPS data key missing: {e}", 5000)
        except Exception as e:
            self.statusBar.showMessage(f"Error parsing GPS data: {e}", 5000)

        return gps_data

    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def convert_to_rational(self, value):
        absolute = abs(value)
        degrees = int(absolute)
        minutes = int((absolute - degrees) * 60)
        seconds = (absolute - degrees - minutes / 60) * 3600 * 100
        return (degrees, 1), (minutes, 1), (int(seconds), 100)

    def format_date_for_exif(self, date_str):
        """Format the date in the EXIF date format."""
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y:%m:%d %H:%M:%S')

    def format_gps_for_exif(self, gps_str):
        lat_str, lon_str = gps_str.split(', ')
        lat = self.convert_to_rational(float(lat_str))
        lon = self.convert_to_rational(float(lon_str))

        return {
            'GPSLatitude': lat,
            'GPSLongitude': lon,
            'GPSLatitudeRef': 'N' if float(lat_str) >= 0 else 'S',
            'GPSLongitudeRef': 'E' if float(lon_str) >= 0 else 'W',
        }

    def is_valid_gps(self, gps_str):
        gps_pattern = re.compile(r'^-?\d+(\.\d+)?, -?\d+(\.\d+)?$')
        return bool(gps_pattern.match(gps_str))

    def apply_batch_edit(self):
        new_date = self.date_edit.text()
        new_gps = self.gps_edit.text()

        if not self.is_valid_date(new_date):
            self.statusBar.showMessage("Invalid date format. Please use YYYY-MM-DD", 5000)
            return
        if not self.is_valid_gps(new_gps):
            self.statusBar.showMessage("Invalid GPS format. Please use decimal degrees (lat, long).", 5000)
            return

        for index in self.image_list_widget.selectedIndexes():
            filename = index.data()
            filepath = os.path.join(self.current_directory, filename)
            self.update_exif_data(filepath, new_date, new_gps)
        self.statusBar.showMessage("Changes applied successfully", 5000)

        indexes = self.image_list_widget.selectedIndexes()
        if len(indexes) == 1:
            self.display_exif_data(indexes)

    def update_exif_data(self, filepath, new_date, new_gps):
        try:
            exif_dict = piexif.load(filepath)

            exif_date = self.format_date_for_exif(new_date)
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date

            exif_gps = self.format_gps_for_exif(new_gps)
            for tag in exif_gps:
                exif_dict['GPS'][piexif.GPSIFD.__dict__[tag]] = exif_gps[tag]

            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, filepath)
        except Exception as e:
            self.statusBar.showMessage(f"Error processing file {filepath}: {e}")

    def handle_empty_space_click(self, item):
        if not self.image_list_widget.selectedIndexes():
            self.image_list_widget.clearSelection()

    def center_window(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))

    def load_images_from_folder(self, folder_path):
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        self.image_loader_thread = ImageLoaderThread(folder_path)
        self.image_loader_thread.progress_update.connect(self.on_progress_update)
        self.image_loader_thread.finished_loading.connect(self.on_finished_loading)
        self.image_loader_thread.start()

    def on_progress_update(self, progress):
        self.progress_bar.setValue(progress)

    def on_finished_loading(self, images):
        self.populate_image_list(images)
        self.progress_bar.hide()

    def populate_image_list(self, images):
        model = QStandardItemModel()
        for image in images:
            model.appendRow(image)

        self.statusBar.showMessage(f"Loaded {model.rowCount()} images from {self.current_directory}", 5000)

        self.image_list_widget.setModel(model)
        self.image_list_widget.selectionModel().selectionChanged.connect(self.on_image_selected)

    def setup_image_list(self):
        self.image_list_widget.setViewMode(QListView.IconMode)
        self.image_list_widget.setIconSize(QSize(100, 100))
        self.image_list_widget.setGridSize(QSize(120, 120))
        self.image_list_widget.setSpacing(10)
        self.image_list_widget.setFlow(QListView.LeftToRight)
        self.image_list_widget.setResizeMode(QListView.Adjust)

        self.image_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.image_list_widget.setDragDropMode(QAbstractItemView.NoDragDrop)

    def setup_config_panel(self):
        # Configuration Group for displaying EXIF data
        exif_group = QGroupBox("EXIF Data")
        exif_layout = QVBoxLayout()
        exif_layout.setSpacing(5)
        exif_layout.setContentsMargins(10, 10, 10, 10)
        self.exif_data_label = QLabel("EXIF data will be shown here")
        exif_layout.addWidget(self.exif_data_label)
        exif_group.setLayout(exif_layout)

        # Configuration Group for batch editing
        edit_group = QGroupBox("Edit EXIF Data")
        edit_layout = QFormLayout()
        edit_layout.setSpacing(5)
        edit_layout.setContentsMargins(5, 10, 5, 10)
        edit_layout.addRow("New Date (YYYY-MM-DD):", self.date_edit)
        edit_layout.addRow("New GPS Coordinates (lat, long):", self.gps_edit)
        edit_layout.addRow(self.apply_btn)
        edit_group.setLayout(edit_layout)

        # Add groups to the configuration layout
        self.config_layout.addWidget(exif_group)
        self.config_layout.addWidget(edit_group)
        self.config_layout.addWidget(self.directory_btn)
        self.config_layout.addStretch()

        self.hide_batch_edit_widgets()

    def convert_to_decimal(self, lat, long):
        return lat[0][0] + lat[1][0] / 60 + lat[2][0] / lat[2][1] / 3600, \
               long[0][0] + long[1][0] / 60 + long[2][0] / long[2][1] / 3600

    def convert_to_degrees(self, value):
        d, m, s = value
        return d[0] / d[1] + m[0] / m[1] / 60 + s[0] / s[1] / 3600


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWin = ImageConfigApp()
    mainWin.show()

    sys.exit(app.exec_())
