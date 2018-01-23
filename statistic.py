"""statistic module"""

import sys
import datetime
from operator import itemgetter
import calendar

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import myLabel
import daylog
import category

class StatWidget(QMainWindow):
    """통계 위젯"""
    def __init__(self, parent=None):
        """initialize"""
        super(StatWidget, self).__init__(parent)
        today = datetime.date.today()
        self.target_year = today.year
        self.target_month = today.month
        self.target_day = today
        self.target_week = today.isocalendar()[1]
        self.monthlog = daylog.monthLog(today.year, today.month)
        self.category = category.Category()
        self.stat_switch = 0
        self.h_devide = 4
        self.initUI()
        self.day_stat()

    def initUI(self):
        """UI 설정"""
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setWindowTitle("통계")

        """버튼 위젯"""
        self.btn_widget = QWidget()
        self.btn_layout = QHBoxLayout()
        self.btn_widget.setLayout(self.btn_layout)
        self.btn_p = QPushButton("<")
        self.btn_layout.addWidget(self.btn_p)
        self.btn_p.clicked.connect(self.prev)
        self.btn_day = QPushButton("Day")
        self.btn_layout.addWidget(self.btn_day)
        self.btn_day.clicked.connect(self.day_button)
        self.btn_week = QPushButton("Week")
        self.btn_layout.addWidget(self.btn_week)
        self.btn_week.clicked.connect(self.week_button)
        self.btn_month = QPushButton("Month")
        self.btn_layout.addWidget(self.btn_month)
        self.btn_month.clicked.connect(self.month_button)
        self.btn_n = QPushButton(">")
        self.btn_layout.addWidget(self.btn_n)
        self.btn_n.clicked.connect(self.next)
        self.layout.addWidget(self.btn_widget)

        """표시 위젯"""
        self.display = myLabel.new("",frame=True)
        self.layout.addWidget(self.display)

        """통계 위젯"""
        self.stat_widget = QWidget()
        self.stat_grid = QGridLayout()
        self.stat_widget.setLayout(self.stat_grid)
        self.layout.addWidget(self.stat_widget)

        """그래프 위젯"""
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

    def day_button(self):
        """일간 버튼을 누를 때"""
        self.stat_switch = 0
        self.target_day = datetime.date.today()
        self.day_stat()

    def day_stat(self):
        """주어진 날짜에 대한 일간 통계"""
        stat_count = day_count(self.monthlog.log[str(self.target_day)], self.category)
        total = 0
        for member in stat_count:
            total += member[1]
        if total < 24 * self.h_devide:
            stat_count.append(['미기록', 24 * self.h_devide - total])
        self.stat_grid = print_stat(self.stat_grid, stat_count)
        self.graphic(stat_count)
        self.display.setText(str(self.target_day))

    def week_button(self):
        """주간 버튼을 누를 때"""
        self.stat_switch = 1
        self.target_day = datetime.date.today()
        self.target_month = self.target_day.month
        self.week_stat()

    def week_stat(self):
        """주어진 주에 대한 통계"""
        day_start = self.target_day - datetime.timedelta(days = self.target_day.weekday())
        long_stat = []
        for i in range(7):
            day = day_start + datetime.timedelta(days = i)
            year = day.year
            month = day.month
            if month == self.target_month:
                day_log = day_count(self.monthlog.log[str(day)],self.category)
            else:
                self.target_month = month
                self.target_year = year
                self.monthlog = daylog.monthLog(year, month)
                self.target_month = month
                day_log = day_count(self.monthlog.log[str(day)], self.category)
            for count in day_log :
                find = False
                for i in range(len(long_stat)):
                    if long_stat[i][0] == count[0]:
                        long_stat[i][1] += count[1]
                        find = True
                if find is False:
                    long_stat.append(count)
        long_stat = sorted(long_stat, key = itemgetter(1))
        long_stat.reverse()
        total = 24 * self.h_devide * 7
        check = 0
        for element in long_stat:
            check += element[1]
        if check < total:
            long_stat.append(['미기록', total - check])
        self.stat_grid = print_stat(self.stat_grid, long_stat)
        self.graphic(long_stat)
        self.display.setText("%s ~ %s" %(str(day_start),
                                        str(day_start + datetime.timedelta(days = 6))))

    def month_button(self):
        """월간 버튼을 누를 때"""
        self.stat_switch = 2
        today = datetime.date.today()
        self.target_year = today.year
        self.target_month = today.month
        self.monthlog = daylog.monthLog(self.target_year, self.target_month)
        self.month_stat()

    def month_stat(self):
        """주어진 달에 대한 통계"""
        days = calendar.monthrange(self.target_year, self.target_month)[1]
        month_stat = []
        for i in range(days):
            day_log = day_count(self.monthlog.log[str(datetime.date(self.target_year,
                                                                   self.target_month, 1+i))], self.category)
            for count in day_log:
                find = False
                for i in range(len(month_stat)):
                    if month_stat[i][0] == count[0]:
                        month_stat[i][1] += count[1]
                        find = True
                if find is False:
                    month_stat.append(count)
        month_stat = sorted(month_stat, key = itemgetter(1))
        month_stat.reverse()
        total = 24 * self.h_devide * days
        check = 0
        for element in month_stat:
            check += element[1]
        if check < total:
            month_stat.append(['미기록', total - check])
        self.stat_grid = print_stat(self.stat_grid, month_stat)
        self.graphic(month_stat)
        self.display.setText("%d 월" %self.target_month)

    def prev(self):
        """이전 버튼"""
        if self.stat_switch < 1: #일간
            self.target_day = self.target_day + datetime.timedelta(days = -1)
            if self.target_day.month < self.target_month: #월간 이동
                self.target_month -= 1
                self.monthlog = daylog.monthLog(self.target_year, self.target_month)
            self.day_stat()

        elif self.stat_switch > 1: #월간
            if self.target_month == 1:
                self.target_month = 12
                self.target_year -= 1
            else:
                self.target_month -= 1
            self.monthlog = daylog.monthLog(self.target_year, self.target_month)
            self.month_stat()

        else: #주간
            self.target_day = self.target_day - datetime.timedelta(days = 7)
            self.week_stat()


    def next(self):
        """이후 버튼"""
        if self.stat_switch < 1: #일간
            self.target_day = self.target_day + datetime.timedelta(days = 1)
            if self.target_day.month > self.target_month: #월간 이동
                self.target_month += 1
                self.monthlog = daylog.monthLog(self.target_year, self.target_month)
            self.day_stat()

        elif self.stat_switch > 1: #월간
            if self.target_month == 12:
                self.target_month = 1
                self.target_year += 1
            else:
                self.target_month += 1
            self.monthlog = daylog.monthLog(self.target_year, self.target_month)
            self.month_stat()

        else: #주간
            self.target_day = self.target_day + datetime.timedelta(days = 7)
            self.week_stat()


    def graphic(self, stat_count):
        """그래프 도시"""
        self.scene.clear()
        total = 0
        for element in stat_count:
            total += element[1]
        set_angle = 1440
        for element in stat_count:
            angle = float(int(-element[1])/total*5760)
            ellipse = QGraphicsEllipseItem(0, 0, 300, 300)
            ellipse.setPos(0, 0)
            ellipse.setStartAngle(set_angle)
            ellipse.setSpanAngle(angle)
            color = QColor(myLabel.get_b(element[0]))
            ellipse.setBrush(color)
            set_angle += angle
            self.scene.addItem(ellipse)

def day_count(daylog, category):
    """일간 통계 반환"""
    total = 0
    count = []
    h_devide = 4
    for i in range(24*h_devide):
        if daylog[i] != '':
            target = category.find(daylog[i])
            find = False
            if len(count) == 0:
                count.append([target, 0])
            for element in count:
                if target == element[0]:
                    element[1] += 1
                    find = True
                    total += 1
            if find is False:
                count.append([target, 1])
                total += 1
    if len(count) > 0:
        count = sorted(count, key = itemgetter(1))
        count.reverse()
    return count

def print_stat(grid, stat_count):
    """통계 결과 도시"""
    for column in range(grid.columnCount()):
        for row in range(2):
            item = grid.itemAtPosition(row, column)
            if item != None:
                widget = item.widget()
                if widget != None:
                    grid.removeWidget(widget)
                    widget.deleteLater()
    x=0
    for member in stat_count:
        label = myLabel.new(member[0], frame = True)
        fcolor = myLabel.get_f(member[0])
        bcolor = myLabel.get_b(member[0])
        label = myLabel.set_color2(label, fcolor, bcolor)
        grid.addWidget(label, 0, x)
        label = myLabel.new(min_convert(member[1]), frame = True)
        label = myLabel.set_color2(label, fcolor, bcolor)
        grid.addWidget(label, 1, x)
        x += 1
    return grid

def min_convert(number):
    """시간 소요를 분 단위로 전환"""
    h_devide = 4
    minute = int(number)*60//h_devide
    hour = minute//60
    minute = minute%60
    day = hour//24
    hour = hour%24
    if day == 0:
        if hour == 0:
            return "%d분" %minute
        else:
            if minute == 0:
                return "%d시간" %hour
            return "%d시간 %d분" %(hour, minute)
    if hour == 0:
        if minute == 0:
            return "%d일" %day
        else:
            return "%d일 %d분" %(day, minute)
    return "%d일 %d시간 %d분" %(day, hour, minute)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stat = StatWidget()
    stat.show()
    sys.exit(app.exec_())
