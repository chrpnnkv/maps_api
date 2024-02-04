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
        self.pt = None
        self.object = None
        self.scale = 0.005
        self.type_flag = True
        self.type = ('Схема', 'map')
        self.types = {'Схема': 'map', 'Гибрид': 'skl', 'Спутник': 'sat'}
        self.change_img()

        self.search_btn.clicked.connect(self.change_coords)
        self.delete_btn.clicked.connect(self.delete_pt)
        self.map_type.currentTextChanged.connect(self.type_change)

        self.keys = [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]
        self.map_type.installEventFilter(self)
        self.search_line.installEventFilter(self)
        self.search_btn.installEventFilter(self)

        self.full_address.hide()
        self.post_code.clicked.connect(self.change_address)

    def change_coords(self):
        search_text = self.search_line.displayText()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": search_text,
            "ll": ','.join(map(str, self.coords)),
            "format": "json"}
        geocoder_response = requests.get(geocoder_api_server, params=geocoder_params)

        if geocoder_response:
            json_response = geocoder_response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
            if toponym:
                self.object = toponym[0]
                self.coords = tuple(map(float, self.object["GeoObject"]["Point"]["pos"].split()))
                self.pt = self.coords
                self.change_img()
                self.full_address.show()
                address = self.object["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
                if self.post_code.isChecked():
                    post_code = self.object["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"].get(
                        "postal_code", False)
                    if post_code:
                        self.full_address.setPlainText(address + ', ' + post_code)
                    else:
                        self.full_address.setPlainText(address + '\n' + 'Нет информации о почтовом индексе')
                else:
                    self.full_address.setPlainText(address)

    def change_img(self):
        self.curr_image = QImage(get_image(self.coords, l=self.type[1], delta=self.scale, pt=self.pt))
        self.images()

    def delete_pt(self):
        self.search_line.setText('')
        self.pt = None
        self.full_address.hide()
        self.change_img()

    def change_address(self):
        if self.full_address.isVisible():
            address = self.object["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
            if self.post_code.isChecked():
                post_code = self.object["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"].get(
                    "postal_code", False)
                if post_code:
                    self.full_address.setPlainText(address + ', ' + post_code)
                else:
                    self.full_address.setPlainText(address + '\n' + 'Нет информации о почтовом индексе')
            else:
                self.full_address.setPlainText(address)

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
            self.type_flag = False
        if event.type() == QEvent.KeyPress:
            if event.key() in self.keys or (
                    int(event.modifiers()) == (Qt.ControlModifier + Qt.AltModifier) and event.key() in (
                    Qt.Key_9, Qt.Key_3)):
                self.search_line.setReadOnly(True)
                self.keyPressEvent(event)
            else:
                self.search_line.setReadOnly(False)
        return super(MainWindow, self).eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.scale > 0.002:
                self.scale /= 2
        if event.key() == Qt.Key_PageDown:
            if self.scale < 0.2:
                self.scale *= 2
        if event.key() == Qt.Key_Up:
            self.coords = (self.coords[0], self.coords[1] + self.scale ** 1.2)
        if event.key() == Qt.Key_Down:
            self.coords = (self.coords[0], self.coords[1] - self.scale ** 1.2)
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
