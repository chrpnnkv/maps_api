import sys
import os
import requests
from PyQt5.QtGui import QImage

def get_image(coords, l='map', delta=0.005):
    map_params = {
        "ll": "{0},{1}".format(*coords),
        "spn": ",".join([str(delta) for _ in range(2)]),
        "l": l
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    if not response:
        sys.exit()

    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)

    qimg = QImage(map_file)
    os.remove(map_file)
    return qimg