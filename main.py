import sys
from io import BytesIO
import requests
import io
from PyQt5.QtGui import QPainter, QColor, QPixmap, QImage, QPen, QTransform
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QLabel, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5 import uic
from get_map_image import get_image

SCREEN_SIZE = (800, 600)
start_coords = (65.344520, 55.439433)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('maps_ui.ui', self)

        self.coords = start_coords
        self.scale = 0.005
        self.curr_image = QImage(get_image(self.coords, delta=self.scale))
        self.images()

    def change_img(self):
        self.curr_image = QImage(get_image(self.coords, delta=self.scale))
        self.images()

    def images(self):
        self.pixmap = QPixmap(self.curr_image)
        self.image.setScaledContents(True)
        self.image.setPixmap(self.pixmap)

        self.width, self.height = self.curr_image.width(), self.curr_image.height()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.scale > 0.002:
                self.scale /= 2
        if event.key() == Qt.Key_PageDown:
            if self.scale < 0.2:
                self.scale *= 2
        if event.key() == Qt.Key_Up:
            self.coords = (self.coords[0], self.coords[1] + self.scale)
        if event.key() == Qt.Key_Down:
            self.coords = (self.coords[0], self.coords[1] - self.scale)
        if event.key() == Qt.Key_Left:
            self.coords = (self.coords[0] - self.scale, self.coords[1])
        if event.key() == Qt.Key_Right:
            self.coords = (self.coords[0] + self.scale, self.coords[1])
        self.change_img()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())



