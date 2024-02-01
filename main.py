import sys
from io import BytesIO
import requests
import io
from PyQt5.QtGui import QPainter, QColor, QPixmap, QImage, QPen, QTransform
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QLabel, QButtonGroup
from PyQt5.QtCore import Qt, QObject, QEvent
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
        self.type_flag = True
        self.type = ('Схема', 'map')
        self.types = {'Схема': 'map', 'Гибрид': 'skl', 'Спутник': 'sat'}
        self.curr_image = QImage(get_image(self.coords, l=self.type[1], delta=self.scale))
        self.images()

        self.map_type.currentTextChanged.connect(self.type_change)
        self.map_type.installEventFilter(self)

    def change_img(self):
        self.curr_image = QImage(get_image(self.coords, l=self.type[1], delta=self.scale))
        self.images()

    def type_change(self):
        if self.type_flag:
            type = self.map_type.currentText()
            self.type = (type, self.types[type])
            self.change_img()
        else:
            self.map_type.setCurrentText(self.type[0])
            self.type_flag = True

    def images(self):
        self.pixmap = QPixmap(self.curr_image)
        self.image.setScaledContents(True)
        self.image.setPixmap(self.pixmap)

        self.width, self.height = self.curr_image.width(), self.curr_image.height()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.map_type:
            self.keyPressEvent(event)
            self.type_flag=False
        return super(MainWindow, self).eventFilter(source, event)

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



