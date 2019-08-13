from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
import sys
from platform import system
from PyQt5 import uic
import requests
import os
import webbrowser
from enum import Enum


ALL_LANGUAGES = ["english","japanese","chinese","translated"]
COMMON_TAGS = ["incest","lolicon","ahegao","shotacon","sweat","blowjob","nakadashi","impregnation","dark skin","footjob","harem","stockings","paizuri"]

tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]


class TagDialog(QDialog, tag_dialog_class):
    
    
    def __init__(self, parent=None,columns = 8, languages = ALL_LANGUAGES):

        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()
        
        self.tableWidget.setColumnCount(columns)
        self.tableWidget.setRowCount(5)
        
        self.tableWidget.setSpan(0,0,1,8)
        self.tableWidget.setSpan(1,len(languages), 1, columns - len(languages))
        
        language_item = QTableWidgetItem("Languages")
        language_item.setTextAlignment(Qt.AlignHCenter)
        self.tableWidget.setItem(0,0,language_item)
        
        self.tableWidget.setSpan(2,0,1,8)
        tag_item = QTableWidgetItem("Common tags")
        tag_item.setTextAlignment(Qt.AlignHCenter)
        self.tableWidget.setItem(2,0,tag_item)
        
        
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        for column,language in enumerate(languages,0):
            self.tableWidget.setCellWidget(1,column, QCheckBox(language))
            
        for index,tag in enumerate(COMMON_TAGS,0):
           self.tableWidget.setCellWidget(3 + index/columns ,index%columns, QCheckBox(tag))
            
    
    def retrieve_checked_cells(self):
        tags = []
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                try:
                    if(self.tableWidget.cellWidget(row,column).isChecked()):
                        tags.append(self.tableWidget.cellWidget(row,column).text())
                        
                except AttributeError:
                    pass
        
        return tags
