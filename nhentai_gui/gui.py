from PyQt5.QtCore import Qt , pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QWidget,QMessageBox,QMainWindow,QAction, QActionGroup,QMenu,QTableWidget,QTableWidgetItem, QFileDialog,QDialog,QCheckBox,QHeaderView, QLineEdit,QStyleFactory,QFrame
import sys
from platform import system
from PyQt5 import uic



form_class = uic.loadUiType("nhentai-downloader.ui")[0]
tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]
settings_dialog_class = uic.loadUiType("config_dialog.ui")[0]


ALL_LANGUAGES = ["english","japanese","chinese","translated"]

COMMON_TAGS = ["incest","lolicon","ahegao","shotacon","sweat","blowjob","nakadashi","impregnation","dark skin","footjob","harem","stockings","paizuri"]



class ConfigDialog(QDialog, settings_dialog_class):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
    
    



class TagDialog(QDialog, tag_dialog_class):
    
    
    def __init__(self, parent=None,columns = 8, languages = ALL_LANGUAGES):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        
        self.buttonBox.accepted.connect(self.retrieve_checked_cells)
        
        
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
        checked_cells = []
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                try:
                    if(self.tableWidget.cellWidget(row,column).isChecked()):
                        checked_cells.append(self.tableWidget.cellWidget(row,column).text())
                        
                except AttributeError:
                    pass
                    
                
        
        
        
        
        print(checked_cells)
        
        
        
        
        
class ThemeAction(QAction):
    App = None
    
    
    def __init__(self,name,main_window,parent = None):
        super().__init__(name,parent)
        self.main_window = main_window
        self.setCheckable(True)
        self.triggered.connect(self.set_theme)
        
        
    def set_theme(self):
        print(f"new theme {self.text()}")
        if(self.text() == "NhentaiDark"):
            self.App.setStyle("Fusion")
            self.App.setPalette(self.configure_pallete())
            
        else:
            self.App.setStyle(self.text())
        
    def configure_pallete(self):
        #dark theme
        palette = QPalette()

        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        return palette
    




class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.location_selection.clicked.connect(self.location_selection_click)
        self.select_tags_button.clicked.connect(self.tags_selection_click)
        
        
        self.actionSettings.triggered.connect(self.settings_click)
        
        self.frame_6.setStyleSheet("#frame_6 {border:0;}")
        self.frame_5.setStyleSheet("#frame_5 {border:0;}")
        
        available_styles_group = QActionGroup(self)
        available_styles_group.setExclusive(True)
        
        for style in QStyleFactory.keys():
            action = ThemeAction(style,self)
            available_styles_group.addAction(action)
            
        available_styles_group.addAction(ThemeAction("NhentaiDark",self))
        
        
        self.menuAppearance.addActions(available_styles_group.actions())
        
    
    def settings_click(self):
        config_dialog = ConfigDialog(None)
        config_dialog.show()
        config_dialog.exec_()
        
        
    def tags_selection_click(self):
        print("tags selection")
        tag_dialog = TagDialog(None)
        tag_dialog.show()
        tag_dialog.exec_()
        
        
    def location_selection_click(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self,"Select save location", "", options=QFileDialog.ShowDirsOnly)
        self.location_directory.setText(directory)
        
        
            

            
app = QApplication(sys.argv)
ThemeAction.App = app

myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
