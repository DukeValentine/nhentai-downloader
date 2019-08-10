from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import *
import sys
from platform import system
from PyQt5 import uic
import os
from enum import Enum



form_class = uic.loadUiType("nhentai-downloader.ui")[0]
tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]
settings_dialog_class = uic.loadUiType("config_dialog.ui")[0]


ALL_LANGUAGES = ["english","japanese","chinese","translated"]

COMMON_TAGS = ["incest","lolicon","ahegao","shotacon","sweat","blowjob","nakadashi","impregnation","dark skin","footjob","harem","stockings","paizuri"]


DOWNLOAD_ACTION = Enum('action','search id favorite')
AFTER_DOWNLOAD = Enum('action','Nothing .cbz .zip')



class NhentaiSettings(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.save_directory = os.getcwd()
        self.log_directory = os.getcwd()
        self.directory = self.save_directory
        self.overwrite = False
        self.download = True
        self.torrent = False
        self.delay = 1.0
        self.threads = 4
        self.retry = 5
        self.after_download = AFTER_DOWNLOAD.Nothing
        self.initial_page = 1
        self.max_page = 0
        self.download_action = DOWNLOAD_ACTION.search
        self.login = None
        self.password = None
        
    

    


class ConfigDialog(QDialog, settings_dialog_class):
    settingsChanged = pyqtSignal(NhentaiSettings)
    #settingsChanged = pyqtSignal()
    
    
    def __init__(self, parent=None,settings = NhentaiSettings()):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.settings = settings
        self.initial_config(settings)
        
        
        
        self.download_end_choice.currentIndexChanged.connect(self.download_choice_change)
        self.download_image_checkbox.stateChanged.connect(self.download_image_check)
        
        self.location_selection_save_config_dialog.clicked.connect(self.location_save_click)
        self.location_selection_log_config_dialog.clicked.connect(self.location_log_click)
        
       
        
        
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.default_settings)
        self.buttonBox.button(QDialogButtonBox.Help).clicked.connect(self.open_help)
    
    def initial_config(self,settings):
        self.location_save_config_dialog.setText(settings.save_directory)
        self.location_log_config_dialog.setText(settings.log_directory)
        
        
        
    def apply_settings(self):
        self.settings.save_directory = self.location_save_config_dialog.text()
        self.settings.log_directory = self.location_log_config_dialog.text()
        self.settingsChanged.emit(self.settings)
        #self.settingsChanged.emit()
        
        
        print("apply")
    
    def default_settings(self):
        print("defaults")
    
    def open_help(self):
        print("help")
        
        
    def download_choice_change(self):
        self.remove_after_checkbox.setEnabled(self.download_end_choice.currentIndex() > 0)
        
    def download_image_check(self):
        self.overwrite_checkbox.setEnabled( self.download_image_checkbox.isChecked())
        
        if(self.overwrite_checkbox.isChecked()):
            self.overwrite_checkbox.setChecked( self.download_image_checkbox.isChecked() == True)
            
    def location_save_click(self):
        directory = QFileDialog.getExistingDirectory(self,"Select save location", "", options=QFileDialog.ShowDirsOnly)
        self.location_save_config_dialog.setText(directory)
        
    def location_log_click(self):
        directory = QFileDialog.getExistingDirectory(self,"Select log location", "", options=QFileDialog.ShowDirsOnly)
        self.location_log_config_dialog.setText(directory)
        
        
        
    
    



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
    


def login_action():
    print("login")


class MyWindowClass(QMainWindow, form_class):

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.tag_dialog = None
        self.config_dialog = ConfigDialog(None)
        self.config_dialog.settingsChanged.connect(self.update_settings)
        
        self.frame_search = self.frame_2
        self.frame_id = self.control_frame2
        self.settings = NhentaiSettings()
    
        
        self.location_selection.clicked.connect(self.location_selection_click)
        self.select_tags_button.clicked.connect(self.tags_selection_click)
        self.login_button.clicked.connect(login_action)
        
        
        
        
        
        
        self.actionSettings.triggered.connect(self.settings_click)
        self.control_frame2.hide()
        
        #self.frame_6.setStyleSheet("#frame_6 {border:0;}")
        #self.frame_5.setStyleSheet("#frame_5 {border:0;}")
        
        
        
        available_styles_group = QActionGroup(self)
        available_styles_group.setExclusive(True)
        
        for style in QStyleFactory.keys():
            action = ThemeAction(style,self)
            available_styles_group.addAction(action)
            
        available_styles_group.addAction(ThemeAction("NhentaiDark",self))
        
        self.search_type_selection.currentIndexChanged.connect(self.search_type_change)
        
        
        self.menuAppearance.addActions(available_styles_group.actions())
        
    def closeEvent(self, event):

        print ("User has clicked the red x on the main window")
        print(self.tag_dialog)
         
        if(self.tag_dialog):
            self.tag_dialog.accept()
            
        if(self.config_dialog):
            self.config_dialog.accept()
            
        event.accept()
        
    def search_type_change(self):
        print(f"now it's {self.search_type_selection.currentIndex()}")
        if(self.search_type_selection.currentIndex() == 1):
            self.frame_2 = self.frame_id
            self.control_frame2.show()
            
        else:
            self.frame_2 = self.frame_search
            self.control_frame2.hide()
        
    
    def settings_click(self):
        self.config_dialog.show()
        self.config_dialog.exec_()
        
    def update_settings(self,new_settings):
        self.settings = new_settings
        print(self.settings.save_directory)
        
        
        
        
    def tags_selection_click(self):
        print("tags selection")
        self.tag_dialog = TagDialog(None)
        self.tag_dialog.show()
        self.tag_dialog.exec_()
        
        
    def location_selection_click(self):

        options = QFileDialog.Options()

        directory = QFileDialog.getExistingDirectory(self,"Select save location", "", options=QFileDialog.ShowDirsOnly)

        self.location_directory.setText(directory)
        
        
            

            
app = QApplication(sys.argv)

ThemeAction.App = app

myWindow = MyWindowClass(None)

myWindow.show()

sys.exit(app.exec_())
