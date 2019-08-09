from PyQt5.QtCore import Qt , pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QWidget,QMessageBox,QMainWindow,QAction, QMenu,QTableWidget,QTableWidgetItem, QFileDialog,QDialog,QCheckBox,QHeaderView
import sys
from platform import system
from PyQt5 import uic



form_class = uic.loadUiType("nhentai-downloader.ui")[0]
tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]

ALL_LANGUAGES = ["english","japanese","chinese","translated"]



class TagDialog(QDialog, tag_dialog_class):
    def __init__(self, parent=None,columns = 8, languages = ALL_LANGUAGES):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()
        
        self.tableWidget.setColumnCount(columns)
        self.tableWidget.setRowCount(2)
        
        self.tableWidget.setSpan(0,0,1,8)
        self.tableWidget.setSpan(1,len(languages), 1, columns - len(languages))
        
        language_item = QTableWidgetItem("Languages")
        language_item.setTextAlignment(Qt.AlignHCenter)
        self.tableWidget.setItem(0,0,language_item)
        
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        for column,language in enumerate(languages,0):
            self.tableWidget.setCellWidget(1,column, QCheckBox(language))
        
        
        
        





class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.location_selection.clicked.connect(self.location_selection_click)
        
        self.select_tags_button.clicked.connect(self.tags_selection_click)
        
        
    def tags_selection_click(self):
        print("tags selection")
        tag_dialog = TagDialog(None)
        tag_dialog.show()
        tag_dialog.exec_()
        
        
        
    def location_selection_click(self):
        options = QFileDialog.Options()
        fileName = QFileDialog.getExistingDirectory(self,"Select save location", "", options=options)
        if fileName:
            print(fileName)
            

            
app = QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
