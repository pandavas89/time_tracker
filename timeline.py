""" draw timeline module"""

import sys
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import daylog
import myLabel
import coordinate
import category
import autosize

class timeWidget(QWidget):
    '''timeline widget'''
    def __init__(self, parent=None):
        super(timeWidget, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

        #기본설정값. 해결책을 찾아볼 것!
        self.spacing = 1
        self.h_devide = 4
        self.c0_width = 55
        self.row_height = 16

        #화면 크기를 감지하여 적절한 column_width를 찾는다.
        self.col_width = autosize.col_width

        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.grid.setSpacing(self.spacing)
        self.elapse_switch = False #elapse input을 off로 설정
        self.l_click = False
        self.blink_switch = False
        time = datetime.datetime.now()
        self.m_hour = time.hour * 4 + time.minute // 15
        self.m_day = datetime.date.today().day
        self.date = datetime.date.today()
        self.monthlog = daylog.monthLog(self.date.year, self.date.month)
        self.monthline()

    def eventFilter(self, source, event):
        '''Mouse Position Tracking'''
        #마우스가 움직일 때
        if event.type() == QEvent.MouseMove:
            self.m_hour = coordinate.x2hour(event.x())
            self.m_day = coordinate.y2day(event.y())
            self.axis_set()
        return QMainWindow.eventFilter(self, source, event)

    def mousePressEvent(self, QMouseEvent):
        '''입력 시작'''
        if QMouseEvent.buttons() == Qt.LeftButton:
            self.start = coordinate.x2hour(QMouseEvent.x()) - 1
            self.s_day = coordinate.y2day(QMouseEvent.y()) + 1
            self.l_click = True

    def axis_set(self):
        '''축에 표기되는 데이터를 갱신'''
        #기존 데이터를 말소
        for i in range(1, 24 * self.h_devide + 1):
            item = self.grid.itemAtPosition(2, i)
            if item != None:
                widget = item.widget()
                widget = myLabel.set_color2(widget, '#000000', '#FFFFFF')
        for i in range(3, self.monthlog.days + 3):
            item = self.grid.itemAtPosition(i, 0)
            if item != None:
                widget = item.widget()
                widget = myLabel.set_color2(widget, '#000000', '#FFFFFF')

        #현재 시간을 반영
        if self.blink_switch is True:
            time = datetime.datetime.now()
            day = time.day + 2
            hour = time.hour
            minute = time.minute
            item = self.grid.itemAtPosition(day, 0)
            if item != None:
                widget = item.widget()
                if widget != None:
                    widget = myLabel.set_color2(widget, '#FFFFFF', '#FF0000')
            slot = hour * 4 + minute // 15
            item = self.grid.itemAtPosition(2, slot + 1)
            if item != None:
                widget = item.widget()
                if widget != None:
                    widget = myLabel.set_color2(widget, '#FFFFFF', '#FF0000')

        #마우스 위치를 반영
        item = self.grid.itemAtPosition(2, self.m_hour)
        if item != None:
            widget = item.widget()
            widget = myLabel.set_color2(widget, '#FFFFFF', '#000000')
        item = self.grid.itemAtPosition(self.m_day+3, 0)
        if item != None:
            widget = item.widget()
            widget = myLabel.set_color2(widget, '#FFFFFF', '#000000')

    def blink(self):
        '''현재 날짜/시간을 표시'''
        if self.blink_switch is True:
            self.blink_switch = False
        else:
            self.blink_switch = True
        self.axis_set()
    def mouseReleaseEvent(self, QMouseEvent):
        '''입력 종료'''
        if self.l_click == True:
            self.end = coordinate.x2hour(QMouseEvent.x()) - 1
            date = datetime.date(self.monthlog.year, self.monthlog.month, self.s_day)
            text, ok = QInputDialog.getText(self, " ", "%s\n%s - %s" %(str(date),
                                            time_convert(min(self.start, self.end)),
                                            time_convert(max(self.start, self.end)+1)))
            if ok:
                if not category.Category().find(text):
                    t_category = category.Category()
                    t_category.load()
                    category_list = list(t_category.fcolor.keys())
                    c_name, ok = QInputDialog.getItem(self, "미분류", "%s(을)를 다음 카테고리로 분류 : " %text,
                                                      category_list, 0, False)
                    if ok:
                        category.Category().update_task(c_name, text)
                self.monthlog.add(date, text, min(self.start, self.end), max(self.start, self.end)+1)
                self.refresh()
        self.l_click = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        editAction = menu.addAction("Category Adjust")
        elapseAction = menu.addAction("Elapse Start")
        elapseClose = menu.addAction("Elapse End")
        delAction = menu.addAction("Delete")
        delAllAction = menu.addAction("Delete All")

        elapseClose.setEnabled(self.elapse_switch)
        elapseAction.setEnabled(not(self.elapse_switch))

        editAction.setEnabled(False)
        delAction.setEnabled(False)
        delAllAction.setEnabled(False)

        item = self.grid.itemAtPosition(self.m_day + 3, self.m_hour)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                target = widget.text()
                date = str(datetime.date(self.monthlog.year, self.monthlog.month,
                                         self.m_day+1))
                editAction.setEnabled(True)
                delAction.setEnabled(True)
                delAllAction.setEnabled(True)

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == editAction:
            #카테고리 편집
            if editAction.isEnabled():
                #선택한 대상이 있을 때
                c_name = category.Category().find(target)
                category_list = list(category.Category().fcolor.keys())
                category_list.remove(c_name)
                text, ok = QInputDialog.getItem(self, "하위항목 이동",
                                                "%s를 %s(으)로부터 이동 : "
                                                %(target, c_name),
                                                category_list, 0, False)
                if ok:
                    category.Category().update_task(text, target)
                    self.refresh()


        elif action == elapseAction:
            text, ok = QInputDialog.getText(self, "지속 일정", "")
            if ok:
                self.elapse_switch = True

        elif action == elapseClose:
            self.elapse_switch = False

        elif action == delAction:
            #선택한 일정을 일정표로부터 삭제한다
            if delAction.isEnabled():
                h_start = self.m_hour - 1
                while self.monthlog.log[date][h_start] == target:
                    h_start -= 1
                h_start += 1

                h_end = self.m_hour - 1
                while self.monthlog.log[date][h_end] == target:
                    h_end += 1

                self.monthlog.delete(date, h_start, h_end)
                self.refresh()

        elif delAllAction.isEnabled():
            #선택한 일정을 완전히 삭제한다
            if widget != None:
                target = widget.text()
                date = str(datetime.date(self.monthlog.year, self.monthlog.month,
                                         self.m_day+1))

                h_start = self.m_hour - 1
                while self.monthlog.log[date][h_start] == target:
                    h_start -= 1
                h_start += 1

                h_end = self.m_hour - 1
                while self.monthlog.log[date][h_end] == target:
                    h_end += 1
                self.monthlog.delete(target, h_start, h_end)
                category.Category().delete_task(target)
                self.refresh()

    def dayline(self, day):
        '''일간 데이터 출력'''
        count = 1
        start = 1
        prev = ''
        date = datetime.date(year=self.monthlog.year, month=self.monthlog.month, day=int(day))
        log = self.monthlog.log[str(date)]
        for h in range(24*self.h_devide):
            if log[h] == '':
                if prev != '':
                    label.setFixedWidth(self.col_width*count+self.spacing*(count-1))
                    label = myLabel.set_color(label)
                    self.grid.addWidget(label, day+2, start, 1, count)
                    prev = ""
                    count = 1
            else:
                if prev == '':
                    label = myLabel.new(log[h], frame=True, schedule=True)
                    count = 1
                    start = h+1
                    prev = log[h]
                else:
                    if prev == log[h]:
                        count += 1
                        if h == 24*self.h_devide - 1:
                            label.setFixedWidth(self.col_width*count+self.spacing*(count-1))
                            label = myLabel.set_color(label)
                            self.grid.addWidget(label, day+2, start, 1, count)
                    else:
                        label.setFixedWidth(self.col_width*count+self.spacing*(count-1))
                        label = myLabel.set_color(label)
                        self.grid.addWidget(label, day+2, start, 1, count)
                        label = myLabel.new(log[h], frame=True, schedule=True)
                        count = 1
                        start = h+1
                        prev = log[h]
                        if h == 24*self.h_devide - 1:
                            label.setFixedWidth(self.col_width*count + self.spacing*(count-1))
                            label = myLabel.set_color(label)
                            self.grid.addWidget(label, day+2, start, 1, count)

    def monthline(self):
        self.frame()
        for i in range(self.monthlog.days):
            self.dayline(i+1)

    def clear(self, row_start=3, column_start=0):
        for row in range(row_start, self.grid.rowCount()):
            for column in range(column_start, self.grid.columnCount()):
                item = self.grid.itemAtPosition(row, column)
                if item != None:
                    widget = item.widget()
                    if widget != None:
                        self.grid.removeWidget(widget)
                        widget.deleteLater()

    def frame(self):
        """일자와 시간을 출력"""
        n2w = "월화수목금토일"
        label = myLabel.new(self.monthlog.month, frame = True)
        label.setFixedHeight(self.row_height)
        self.grid.addWidget(label, 0, 1, 1, 24*self.h_devide)
        for h in range(24*self.h_devide):
            if h%self.h_devide == 0 :
                label = myLabel.new(h//self.h_devide, frame = True)
                label.setFixedWidth(self.col_width*4+self.spacing*3)
                label.setFixedHeight(self.row_height)
                self.grid.addWidget(label, 1, h+1, 1, self.h_devide)
            label = myLabel.new(h%self.h_devide*15, frame = True)
            label.setFixedWidth(self.col_width)
            label.setFixedHeight(self.row_height)
            self.grid.addWidget(label, 2, h+1)
        for day in range(self.monthlog.days):
            date = datetime.date(self.monthlog.year, self.monthlog.month, day+1)
            label = myLabel.new("%d (%s)" %(date.day, n2w[date.weekday()]), frame = True)
            label.setFixedWidth(self.c0_width)
            label.setFixedHeight(self.row_height)
            self.grid.addWidget(label, day+3, 0)

    def refresh(self):
        self.clear()
        self.monthline()

    def p_month(self):
        year = self.monthlog.year
        month = self.monthlog.month
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        self.monthlog = daylog.monthLog(year, month)
        self.clear(0, 0)
        self.monthline()

    def n_month(self):
        year = self.monthlog.year
        month = self.monthlog.month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        self.clear(0, 0)
        self.monthlog = daylog.monthLog(year, month)
        self.monthline()

def time_convert(time):
    time = int(time)
    hour = time // 4
    minute = time % 4 * 15
    if minute == 0:
        return "%d:00" %hour
    return "%d:%d" %(hour, minute)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tWidget = timeWidget()
    tWidget.show()
    tWidget.move(10,10)
    sys.exit(app.exec_())
