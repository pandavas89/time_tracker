#label control

from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import category

def new(text,align = 0, frame=False, schedule=False):
    label = QLabel(str(text))
    if schedule:
        label.setToolTip(str(text))
    label.setMouseTracking(True)

    if frame == True :
        label.setFrameStyle(QFrame.Panel)

    if align == 0 :
        label.setAlignment(Qt.AlignCenter)
    elif align == 1:
        label.setAlignment(Qt.AlignLeft)
    elif align == 2:
        label.setAlignment(Qt.AlignRight)

    label.setMouseTracking(True)
    return label

def get_f(c_name):
    if c_name is not False and c_name != '미기록':
        return category.Category().fcolor[c_name]
    else:
        return "#000000"

def get_b(c_name):
    if c_name is not False and c_name != '미기록':
        return category.Category().bcolor[c_name]
    else:
        return "#FFFFFF"


def categorize(text):
    """find category from label"""
    Category = category.Category()
    for key in Category.categories:
        if text in Category.categories[key]:
            return key
    return False

def set_color(targetLabel):
    text = targetLabel.text()
    c_name = categorize(text)
    fColor = get_f(c_name)
    bColor = get_b(c_name)
    pal = QPalette()
    pal.setColor(QPalette.Foreground,QColor(fColor))
    pal.setColor(QPalette.Background,QColor(bColor))
    targetLabel.setPalette(pal)
    targetLabel.setAutoFillBackground(True)
    return targetLabel

def set_color2(targetLabel, fColor, bColor):
    pal = QPalette()
    pal.setColor(QPalette.Foreground,QColor(fColor))
    pal.setColor(QPalette.Background,QColor(bColor))
    targetLabel.setPalette(pal)
    targetLabel.setAutoFillBackground(True)
    return targetLabel

if __name__ == "__main__" :
    new("hello world")
