'''recognize monitor resolution'''

import setting
from PyQt5.QtWidgets import QApplication

h_devide = 4
c0_width = 55

app = QApplication([])
screen_resolution = app.desktop().screenGeometry()
width = screen_resolution.width()
col_width = int((width - c0_width)*0.95//(24*h_devide))
