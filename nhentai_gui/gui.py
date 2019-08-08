from PyQt5.QtCore import Qt , pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QWidget,QMessageBox,QMainWindow,QAction, QMenu,QTableWidget,QTableWidgetItem, QFileDialog,QDialog
import sys
from platform import system
from PyQt5 import uic



form_class = uic.loadUiType("nhentai-downloader.ui")[0]
tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]



class TagDialog(QDialog, tag_dialog_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)





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
