import sys
import sqlite3
import os
#imported for shelve - sqlite3 migration only!
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import myLabel

class Category():
    '''category structure'''
    def __init__(self):
        self.categories = {}
        self.fcolor = {}
        self.bcolor = {}

        #file path 설정 : Google Drive API 사용시 변경할 것!
        if getattr(sys, 'frozen', False):
            log_path = os.path.dirname(sys.executable)
        elif __file__:
            log_path = os.path.dirname(__file__)
        file_name = 'daylog.db'
        self.DB_PATH = os.path.join(log_path, file_name)
        self.load()

        #기존 cateogry가 존재하지 않으면 수면 카테고리를 강제 생성
        if len(self.categories) < 1:
            self.add_category('수면')

    def load(self):
        '''sqlite DB와 연결하여 카테고리 정보를 가져온다'''

        #sqlite DB 연결
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #카테고리 테이블이 존재하지 않으면 생성한다.
        query = 'create table if not exists categories'
        query += '(category text PRIMARY KEY, fcolor text, bcolor text)'
        cursor.execute(query)

        #태스크 테이블이 존재하지 않으면 생성한다.
        query = 'create table if not exists tasks'
        query += '(task text UNIQUE, category text)'
        cursor.execute(query)

        #카테고리 테이블로부터 fcolor, bcolor dict를 채운다.
        query = 'select * from categories'
        cursor.execute(query)
        datas = cursor.fetchall()
        self.fcolor.clear()
        self.bcolor.clear()
        for data in datas:
            self.fcolor[data[0]] = data[1]
            self.bcolor[data[0]] = data[2]

        #tasks 테이블로부터 categories dict를 채운다.
        for key in self.fcolor:
            query = 'select task from tasks where category = "%s"' %key
            cursor.execute(query)
            datas = cursor.fetchall()

            #1개짜리 튜플의 리스트를 str 리스트로 전환한다
            r_datas = []
            for data in datas:
                r_datas.append(data[0])
            self.categories[key] = r_datas

    def add_category(self, name):
        '''새로운 카테고리를 추가한다'''
        self.categories[name] = []
        self.fcolor[name] = '#000000'
        self.bcolor[name] = '#FFFFFF'
        self.update_category(name)
        self.load()

    def delete_category(self, name):
        '''카테고리를 삭제한다'''

        #sqlite DB와 연결한다.
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #categories 테이블을 업데이트한다.
        query = 'delete from categories where category = "%s"' %name
        cursor.execute(query)
        connect.commit()
        connect.close()

        self.load()

    def update_category(self, name):
        ''' 카테고리 정보를 업데이트한다'''

        #sqlite DB와 연결한다.
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #categories 테이블을 업데이트한다.
        query = 'insert or replace into categories (category, fcolor, bcolor)'
        query += 'values ("%s", "%s", "%s")' %(name, self.fcolor[name], self.bcolor[name])
        cursor.execute(query)
        connect.commit()
        connect.close()
        self.load()

    def update_task(self, category, task):
        '''새로운 일정을 추가한다'''

        #sqlite DB와 연결한다.
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #tasks 테이블을 업데이트한다.
        query = 'insert or replace into tasks (task, category)'
        query += 'values ("%s", "%s")' %(task, category)
        cursor.execute(query)
        connect.commit()
        connect.close()
        self.load()

    def delete_task(self, task):
        '''일정을 삭제한다'''

        #sqlite DB와 연결한다.
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #tasks 테이블을 업데이트한다.
        query = 'delete from tasks where task = "%s" ' %task
        cursor.execute(query)
        connect.commit()
        connect.close()
        self.load()

    def find(self, task):
        for key in self.categories:
            if task in self.categories[key]:
                return key
        return False

    def migrate(self):
        '''shelve-sqlite3 migration code'''
        db = shelve.open('category')
        self.fcolor = db['fcolor']
        self.bcolor = db['bcolor']
        self.categories = db['categories']
        for key in self.fcolor:
            self.update_category(key)
            for task in self.categories[key]:
                self.update_task(key, task)

class tab_category(QTabWidget):
    '''tab 방식의 새로운 category manager'''
    def __init__(self, parent=None):
        super(tab_category, self).__init__(parent)
        self.category = Category()
        self.count = 0

        self.resize(400, 250)
        self.setWindowTitle("카테고리 관리")

        self.tab = {}
        self.grid = {}
        self.example = {}
        self.f_btn = {}
        self.b_btn = {}
        self.lists = {}
        for key in self.category.categories:
            self.set_tab(key)


    def set_tab(self, name):
        self.tab[name] = QWidget()
        tab = self.tab[name]
        self.grid[name] = QGridLayout()
        self.setTabText(self.count, name)
        tab.setLayout(self.grid[name])
        self.example[name] = myLabel.new(name, frame=True)
        self.grid[name].addWidget(self.example[name], 0, 0)

        #카테고리 색상 설정부
        self.f_btn[name] = QPushButton()
        self.f_btn[name].clicked.connect(self.pick_color)
        self.b_btn[name] = QPushButton()
        self.b_btn[name].clicked.connect(self.pick_color)
        self.grid[name].addWidget(self.f_btn[name], 0, 1)
        self.grid[name].addWidget(self.b_btn[name], 0, 2)

        #카테고리 일정 리스트
        self.lists[name] = QListWidget()
        self.grid[name].addWidget(self.lists[name], 1, 0, 3, 1)
        self.set_task(name)
        self.set_color(name)

        #일정 관리 버튼
        task_add_btn = QPushButton("일정 추가")
        task_add_btn.clicked.connect(self.add_task)
        task_del_btn = QPushButton("일정 삭제")
        task_del_btn.clicked.connect(self.del_task)
        task_move_btn = QPushButton("일정 이동")
        task_move_btn.clicked.connect(self.move_task)
        self.grid[name].addWidget(task_add_btn, 1, 1)
        self.grid[name].addWidget(task_del_btn, 2, 1)
        self.grid[name].addWidget(task_move_btn, 3, 1)

        #카테고리 관리 버튼
        cat_add_btn = QPushButton("카테고리 추가")
        cat_add_btn.clicked.connect(self.add_category)
        cat_del_btn = QPushButton("카테고리 삭제")
        cat_del_btn.clicked.connect(self.del_category)
        cat_rename_btn = QPushButton("이름 바꾸기")
        cat_rename_btn.clicked.connect(self.rename_category)
        self.grid[name].addWidget(cat_add_btn, 1, 2)
        self.grid[name].addWidget(cat_del_btn, 2, 2)
        self.grid[name].addWidget(cat_rename_btn, 3, 2)
        self.addTab(self.tab[name], name)
        self.count += 1

    def get_parent(self, host):
        '''host 인자를 전달받는다'''
        self.host = host

    def refresh(self):
        '''host의 t_widget을 갱신한다'''
        self.host.t_widget.refresh()

    def set_task(self, c_name):
        '''카테고리의 일정 리스트를 업데이트한다'''
        self.lists[c_name].clear()
        if len(self.category.categories[c_name]) > 0:
            for task in self.category.categories[c_name]:
                self.lists[c_name].addItem(task)
            self.lists[c_name].repaint()
        else:
            self.lists[c_name].repaint()


    def set_color(self, c_name):
        '''카테고리 매니저의 색상을 업데이트한다'''
        self.example[c_name] = myLabel.set_color2(self.example[c_name],
                                                self.category.fcolor[c_name],
                                                self.category.bcolor[c_name])
        self.f_btn[c_name].setStyleSheet("background-color : %s;" %self.category.fcolor[c_name])
        self.b_btn[c_name].setStyleSheet("background-color : %s;" %self.category.bcolor[c_name])
        try:
            self.refresh()
        except:
            pass

    def pick_color(self):
        '''색상을 변경한다(폰트, 배경색)'''
        #sender()로부터 편집 대상을 확인한다.
        for key in self.f_btn:
            if self.sender() == self.f_btn[key]:
                c_name = key
                pos = 'F'
        for key in self.b_btn:
            if self.sender() == self.b_btn[key]:
                c_name = key
                pos = 'B'

        #대상의 색상을 편집한다.
        if pos == 'F':
            self.category.fcolor[c_name] = QColorDialog.getColor().name()
        else:
            self.category.bcolor[c_name] = QColorDialog.getColor().name()
        #대상을 업데이트하고 화면을 갱신한다.
        self.category.update_category(c_name)
        self.set_color(c_name)

    def add_task(self):
        '''일정을 추가한다'''
        #현재 탭을 확인한다.
        c_index = self.currentIndex()
        c_name = self.tabText(c_index)
        #새로운 일정을 입력한다.
        task, ok = QInputDialog.getText(self, "새로운 일정 추가", "새로운 일정 : ")
        if ok:
            self.category.update_task(c_name, task)
            #화면을 갱신한다.
            self.set_task(c_name)

    def del_task(self):
        '''일정을 삭제한다'''
        #현재 탭을 확인한다.
        c_index = self.currentIndex()
        c_name = self.tabText(c_index)
        #QListWidget이 선택되었는지 확인
        if self.lists[c_name].currentRow() > 0:
            #선택된 일정을 확인하고 삭제한다.
            task_selection = self.lists[c_name].currentItem().text()
            self.category.delete_task(task_selection)
            #화면을 갱신한다.
            self.set_task(c_name)
        else:
            msg = QMessageBox.warning(self, "일정 선택되지 않음!",
                                      "일정이 선택되지 않았습니다.")

    def move_task(self):
        '''일정을 이동한다'''
        #현재 탭을 확인한다.
        c_index = self.currentIndex()
        c_name = self.tabText(c_index)
        #QListWidget이 선택되었는지 확인
        if self.lists[c_name].currentRow() > -1:
            task = self.lists[c_name].currentItem().text()
            c_list = self.category.fcolor.keys()
            target, ok = QInputDialog.getItem(self, "일정 이동",
                                              "이동시킬 카테고리를 선택해 주세요",
                                              c_list, editable=False)
            if ok:
                self.category.update_task(target, task)
                self.set_task(c_name)
                self.set_task(target)
            else:
                msg = QMessageBox.warning(self, "일정 선택되지 않음!",
                                          "일정이 선택되지 않았습니다.")
    def add_category(self):
        '''신규 카테고리를 추가한다'''
        #신규 카테고리명을 입력받는다.
        c_name, ok = QInputDialog.getText(self, "신규 카테고리",
                                          "신규 카테고리명을 입력해주세요.")
        #중복되는 카테고리명인 경우
        if c_name in self.category.fcolor.keys():
            msg = QMessageBox.warning(self, "중복되는 카테고리",
                                      "이미 존재하는 카테고리 이름입니다.")
        else:
            #카테고리를 추가한다.
            self.category.add_category(c_name)
            #화면을 갱신한다.
            self.set_tab(c_name)

    def del_category(self):
        '''기존 카테고리를 제거한다'''
        #카테고리명을 감지한다.
        c_index = self.currentIndex()
        c_name = self.tabText(c_index)

        #카테고리 하위 일정의 수를 감지한다.
        task_count = len(self.category.categories[c_name])

        #카테고리 하위 항목이 있을 때
        if task_count > 0:
            text = "%d개의 하위항목이 있습니다. 다른 카테고리로 이동합니까?" %task_count
            msg = QMessageBox.question(self, "하위항목 존재", text,
                                       QMessageBox.Yes | QMessageBox.No)

            #일정을 다른 카테고리로 이동한다.
            if msg == QMessageBox.Yes:
                c_list = list(self.category.fcolor.keys())
                c_list.remove(c_name)
                target, ok = QInputDialog.getItem(self, "이동할 카테고리",
                                                  "이동할 카테고리를 선택해 주세요",
                                                  c_list, editable=False)
                if ok:
                    #일정을 이동시킨다.
                    for task in self.category.categories[c_name]:
                        self.category.update_task(target, task)
                    self.category.delete_category(c_name)
                    self.removeTab(c_index)
                    self.set_task(target)

            #일정을 포함하여 삭제한다.
            else:
                for task in self.category.categories[c_name]:
                    self.category.delete_task(task)
                self.category.delete_category(c_name)
                self.removeTab(c_index)
        #카테고리 하위 항목이 없을 때
        else:
            self.category.delete_category(c_name)
            self.removeTab(c_index)

    def rename_category(self):
        '''카테고리의 이름을 변경한다'''

        #현재 탭을 감지한다.
        c_index = self.currentIndex()
        c_name = self.tabText(c_index)

        new_name, ok = QInputDialog.getText(self, "이름 변경",
                                            "새로운 카테고리명을 입력하세요")
        if ok:
            if new_name in list(self.category.fcolor.keys()):
                msg = QMessageBox(self,"존재하는 이름",
                                  "이미 존재하는 카테고리명입니다")
            else:
                #일정을 옮긴다.
                try :
                    if len(self.category.categories[c_name]) > 0:
                        for task in self.category.categories[c_name]:
                            self.category.update_task(new_name, task)
                except :
                    pass
                #카테고리 색 설정을 옮긴다.
                self.category.add_category(new_name)
                self.category.fcolor[new_name] = self.category.fcolor[c_name]
                self.category.bcolor[new_name] = self.category.bcolor[c_name]
                #신규 카테고리를 생성한다.
                self.category.update_category(new_name)
                #기존 카테고리를 삭제한다.
                self.category.delete_category(c_name)
                #화면을 갱신한다.
                self.set_tab(new_name)
                self.removeTab(c_index)
                self.category.load()

if __name__ == "__main__":
    application = QApplication(sys.argv)
    #category_widget = categoryWidget()
    category_widget = tab_category()
    category_widget.show()
    sys.exit(application.exec_())
