# -*- coding: utf-8 -*-

import sqlite3
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.conn = sqlite3.connect('words.db')

        self.cur = self.conn.cursor()
        words = []
        reads = []

        tables = []
        for table in self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
            tables.append(str(table)[2:-3])
        if 'recent_game' in tables:
            tables.remove('recent_game')    
        if 'downloaded_word' in tables:
            tables.remove('downloaded_word')
        if 'download_persent' in tables:
            tables.remove('download_persent')
        if 'sqlite_sequence' in tables:
            tables.remove('sqlite_sequence')

        if tables:
            query = "select word from "+str(tables[0])
            for word in self.cur.execute(query):
                words.append(str(word)[2:-3])

            query = "select read_word from "+str(tables[0])
            for read in self.cur.execute(query):
                reads.append(str(read)[2:-3])

        self.read_and_word = {
            'word': words,
            'read_word': reads
        }
        self.column_idx_lookup = {'word': 0, 'read_word': 1}

        self.cb = QComboBox(self)
        for table in tables:
            self.cb.addItem(table)
        self.cb.currentTextChanged.connect(self.read_data)
        
        table_groupbox = QGroupBox('테이블 선택')
        input_groupbox = QGroupBox('')
        word_groupbox = QGroupBox('단어')
        read_groupBox = QGroupBox('읽는 법')
        self.word_edit = QLineEdit()
        self.read_edit = QLineEdit()
        self.table_edit = QLineEdit()

        input_button = QPushButton('등록', self)
        input_button.clicked.connect(self.insert_data)
        table_create_button = QPushButton('추가', self)
        table_create_button.clicked.connect(self.create_table)
        table_remove_button = QPushButton('테이블 삭제', self)
        table_remove_button.clicked.connect(self.remove_table)
        
        grid_table = QGridLayout()
        grid_input = QGridLayout()
        grid_word = QGridLayout()
        grid_read = QGridLayout()
        grid = QGridLayout()

        grid_word.addWidget(self.word_edit, 0, 0)
        grid_read.addWidget(self.read_edit, 0, 0)
        grid_table.addWidget(self.cb, 0, 0)
        grid_table.addWidget(self.table_edit, 1, 0)
        grid_table.addWidget(table_create_button, 2, 0)
        grid_table.addWidget(table_remove_button, 3, 0)

        table_groupbox.setLayout(grid_table)
        input_groupbox.setLayout(grid_input)
        word_groupbox.setLayout(grid_word)
        read_groupBox.setLayout(grid_read)

        grid_input.addWidget(word_groupbox, 1, 0)
        grid_input.addWidget(read_groupBox, 1, 1)
        grid_input.addWidget(input_button, 2, 1)
        grid.addWidget(table_groupbox, 0, 0)
        grid.addWidget(input_groupbox, 1, 0)

        self.setLayout(grid)
        self.setWindowTitle('단어입력')
        self.setGeometry(300, 300, 300, 400)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(200, 290)
        self.tableWidget.setRowCount(len(reads))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setTableWidgetData()

        self.tableWidget.itemDoubleClicked.connect(self.set_remove_item)

        grid.addWidget(self.tableWidget, 2, 0)

        self.show()
    
    def create_table(self):
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS " + self.table_edit.text() +"(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text, read_word text)")
            self.cb.addItem(self.table_edit.text())
            self.cb.setCurrentText(self.table_edit.text())
            self.table_edit.setText("")
        except:
            self.table_edit.setText("이 이름은 사용 불가")
        
    def remove_table(self):
        self.cur.execute("drop table "+ self.cb.currentText())
        self.cb.removeItem(self.cb.currentIndex())
        self.conn.commit()
        self.cb.setCurrentIndex(0)
        self.read_data()

    def insert_data(self):
        query = "INSERT into "+self.cb.currentText()+"(word, read_word) values (?, ?);"
        self.cur.execute(query,(self.word_edit.text(), self.read_edit.text()))
        self.word_edit.setText("")
        self.read_edit.setText("")
        self.conn.commit()
        self.read_data()

    def read_data(self):
        table_name = self.cb.currentText()
        words = []
        reads = []
        query = "select word from " + table_name
        for word in self.cur.execute(query):
            words.append(str(word)[2:-3])

        query = "select read_word from " + table_name
        for read in self.cur.execute(query):
            reads.append(str(read)[2:-3])

        self.read_and_word['word'] = words
        self.read_and_word['read_word'] = reads

        self.tableWidget.setRowCount(len(reads))
        self.setTableWidgetData()
    
    def set_remove_item(self):
        print(self.tableWidget.selectedItems()[0].text())
        colum = ''
        if self.tableWidget.selectedItems()[0].text() in self.read_and_word['word']:
            colum = "word"
        else:
            colum ="read_word"
        search_item = self.tableWidget.selectedItems()[0].text()
        print(self.cb.currentText())
        print(search_item)
        self.cur.execute("delete from " + self.cb.currentText() + " where "+colum + "= \"" + search_item + "\"")
        self.conn.commit()
        self.read_data()
    
    def setTableWidgetData(self):
        column_headers = ['단어', '읽는 법']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        for k, v in self.read_and_word.items():
            col = self.column_idx_lookup[k]
            for row, val in enumerate(v):
                item = QTableWidgetItem(val)
                if col == 2:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                self.tableWidget.setItem(row, col, item)

        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = ''
    ex = ''
    app = QApplication(sys.argv)   
    ex = MyApp()      
    app.exec_()