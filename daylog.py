'''Monthly Lod Data Structure'''

import datetime
import calendar
import os
import sqlite3
import sys

class monthLog():
    '''월간 데이터 구조체'''
    def __init__(self, year, month):
        '''initialize'''
        self.year = year
        self.month = month
        #목표 월의 날짜 수를 인지한다.
        self.days = calendar.monthrange(year,month)[1]

        #한 시간을 몇 개로 나누는지 정의한다 : option module 개선을 통해 진행예정
        self.h_devide = 4

        #하루의 빈 리스트를 만든다.
        self.blank_log = []
        for t in range(24*self.h_devide):
            self.blank_log.append('')

        #한 달치의 빈 저장구조(dict)를 만든다
        self.log = {}
        for day in range(self.days):
            date = str(datetime.date(year = self.year, month = self.month, day = day + 1))
            self.log[date] = self.blank_log

        #경로를 설정 : option module로 옮길 것인지?

        #sqlite DB 위치와 이름 설정 : PyInstaller에 의한 경로 변경 방지
        if getattr(sys, 'frozen', False):
            log_path = os.path.dirname(sys.executable)
        elif __file__:
            log_path = os.path.dirname(__file__)

        FILE_NAME = 'daylog.db'
        self.DB_PATH = os.path.join(log_path, FILE_NAME)

        #기존 데이터가 있으면 반영한다
        self.load()
        #존재하지 않는 데이터 row를 생성한다.
        for day in range(self.days):
            date = datetime.date(self.year, self.month, day+1)
            self.save(str(date))

    def load(self):
        '''DB로부터 데이터를 가져온다'''
        #sqlite DB와 연결
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #DB 내에 daylog 테이블이 없으면 만든다.
        query = "create table if not exists daylog"
        query += "(date date PRIMARY KEY,"
        for i in range(24*self.h_devide):
            query += ("h%d text," %i)
        query = query[:-1]
        query += ")"
        cursor.execute(query)

        #존재하는 데이터를 출력한다.
        query = "select * from daylog"
        cursor.execute(query)
        output = cursor.fetchall()

        #불러온 데이터 중 기준에 맞는 것을 추려낸다.
        first_day = datetime.date(year = self.year, month = self.month, day = 1)
        last_day = datetime.date(year = self.year, month = self.month, day = self.days)
        for logline in output:
            #str을 다시 datetime object로 환원한다. : 연산이 이렇게 복잡해야 하는가?
            date = datetime.datetime.strptime(logline[0], "%Y-%m-%d")
            date = datetime.date(date.year, date.month, date.day)
            if date >= first_day :
                if date <= last_day :
                    self.log[logline[0]] = list(logline[1:])
        connect.close()

    def save(self, date):
        '''특정 일자의 변동을 DB에 저장한다'''

        #sqlite DB와 연결한다.
        connect = sqlite3.connect(self.DB_PATH)
        cursor = connect.cursor()

        #전달받은 일자를 str로 전환한다.
        date = str(date)

        #sqlite query를 작성한다.
        query = 'insert or replace into daylog (date,'
        for i in range(24*self.h_devide):
            query += ("h%d,"%i)
        query = query[:-1]
        query += (") values ('%s', " %date)

        for i in range(24*self.h_devide):
            #미입력 값일 때 blank로 출력한다.
            if self.log[date][i] == '':
                query += "'',"
            #값이 존재할 때 값을 입력한다.
            else:
                query += ('"%s",' %self.log[date][i])
        #입력 일자의 조건문을 제시한다.
        query = query[:-1]
        query += ")"

        #query를 실행하고 연결을 종료한다.
        cursor.execute(query)
        connect.commit()
        connect.close()

    def add(self, date, content, start, end):
        '''일정을 추가한다'''
        date = str(date)
        for h in range(start, end):
            self.log[str(date)][h] = content
        self.save(str(date))
        self.load()

    def delete(self, date, h_start, h_end):
        '''지정된 범위의 일정을 제거한다'''
        for hour in range(h_start, h_end):
            self.log[str(date)][hour] = ''
        self.save(str(date))
        self.load()



if __name__ == "__main__":
    mLog = monthLog(datetime.date.today().year,datetime.date.today().month)
    while True:
        control = input("command : ")
        if control == "save":
            mLog.save(datetime.date.today())

        elif control == "quit":
            break

        elif control == "add":
            task = input("current task : ")
            start = int(input("start : "))
            end = int(input("end : "))
            check = input("%s/%s~%s"%(task, start, end))
            if check == "yes":
                mLog.add(datetime.date.today(), task, start, end)

        elif control == 'print':
            print(datetime.date.today(),'\n', mLog.log[str(datetime.date.today())])

        elif control == 'load':
            mLog.load()
