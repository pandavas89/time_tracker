import sqlite3
import os

'''setting module'''
class Setting():
    '''manages settings'''
    def __init__(self):
        '''setting initialize'''
        #DB 경로를 찾는다.
        path = os.path.dirname(__file__)
        log_path = os.path.join(path, 'log')
        file_name = 'setting.db'
        self.DB_PATH = os.path.join(log_path, file_name)

        #sqlite DB와 연결
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #settings 테이블이 존재하지 않으면 생성한다.
        query = 'create table if not exists settings'
        query += '(name text PRIMARY KEY, type text, value text)'
        cursor.execute(query)

        #존재하는 모든 데이터를 가져온다.
        query = 'select * from settings'
        cursor.execute(query)
        datas = cursor.fetchall()
        self.type = {}
        self.value = {}
        for data in datas:
            self.type[data[0]] = data[1]
            self.value[data[0]] = data[2]
        connect.close()

    def get_val(self, name):
        '''data output'''
        value = self.value[name]
        if self.type[name] == 'int':
            return int(value)
        elif self.type[name] == 'bool':
            return bool(value)
        else:
            return value

    def save_val(self, name):
        connect = sqlite3.connect(self.DB_PATH)
        cursor = sonnect.cursor()

        query = 'insert or replace into categories (name, type, value)'
        query += 'values ("%s", "%s", "%s")'%(name, self.type[name], self.value[name])
        cursor.execute(query)
        connect.commit()
        connec.close()

    def add_val(self, name, s_type, value):
        self.value[name] = value
        self.type[name] = s_type
        self.save_val(name)
