'''Time Tracker v_0.9.2, for User Test'''

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import sys

import timeline
import category
import statistic

class TimeTracker(QMainWindow):
    '''time tracker desktop application v_0.9.2.'''
    def __init__(self, parent=None):
        super(TimeTracker, self).__init__(parent)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.grid = QGridLayout()
        main_widget.setLayout(self.grid)

        #timer operation
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink)
        self.timer.start(350)

        self.init_ui()
        self.move(10, 10)

        icon = QIcon()
        icon.addPixmap(QPixmap('houglass_icon.ico'))
        self.setWindowIcon(QIcon(icon))

    def init_ui(self):
        '''set UI'''
        self.setWindowTitle('Time Tracker v_0.9.2')

        self.t_widget = timeline.timeWidget()
        self.grid.addWidget(self.t_widget, 1, 0, 1, 2)

        self.bar = self.menuBar()
        self.category_action = QAction('category')
        self.category_action.setShortcut('Ctrl+E')
        self.bar.addAction(self.category_action)
        self.category_action.triggered.connect(self.edit_category)

        self.statistic_action = QAction("statistic")
        self.statistic_action.setShortcut("Ctrl+P")
        self.bar.addAction(self.statistic_action)
        self.statistic_action.triggered.connect(self.statistic_show)

        self.p_button = QPushButton("<")
        self.p_button.clicked.connect(self.p_month)
        self.grid.addWidget(self.p_button, 0, 0)

        self.n_button = QPushButton(">")
        self.n_button.clicked.connect(self.n_month)
        self.grid.addWidget(self.n_button, 0, 1)

    def edit_category(self):
        '''opens the category edit window'''
        self.category_widget = category.tab_category()
        self.category_widget.get_parent(self)
        self.category_widget.move(800, 100)
        self.category_widget.show()

    def statistic_show(self):
        '''opens the statistic window'''
        self.stat_widget = statistic.StatWidget()
        self.stat_widget.show()

    def p_month(self):
        '''moves to previous month'''
        self.t_widget.p_month()

    def n_month(self):
        '''moves to next month'''
        self.t_widget.n_month()

    def blink(self):
        self.t_widget.blink()

if __name__ == "__main__":
    application = QApplication(sys.argv)
    main_widget = TimeTracker()
    main_widget.show()
    sys.exit(application.exec_())
