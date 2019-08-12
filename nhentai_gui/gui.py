from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter
from PyQt5.QtWidgets import *
import sys
from platform import system
from PyQt5 import uic
import os
import webbrowser
from enum import Enum



form_class = uic.loadUiType("nhentai-downloader.ui")[0]
tag_dialog_class = uic.loadUiType("tags_selection.ui")[0]
settings_dialog_class = uic.loadUiType("config_dialog.ui")[0]
thumbnail_class = uic.loadUiType("doujinshi_thumbnail.ui")[0]



ALL_LANGUAGES = ["english","japanese","chinese","translated"]

COMMON_TAGS = ["incest","lolicon","ahegao","shotacon","sweat","blowjob","nakadashi","impregnation","dark skin","footjob","harem","stockings","paizuri"]


DOWNLOAD_ACTION = Enum('action','search id favorite')
AFTER_DOWNLOAD = Enum('action','Nothing .cbz .zip')


class DoujinshiThumbnail(QWidget,thumbnail_class):
    def __init__(self, path,parent=None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        pic = QPixmap(path)
        self.label.setPixmap(pic)
        
        #QStackedWidget().in
        
        
    def mousePressEvent(self, event):
        self.checkBox.setChecked(not self.checkBox.isChecked())
        


class ImgWidget1(QLabel):

    def __init__(self,path,parent=None):
        super(ImgWidget1, self).__init__(parent)
        pic = QPixmap(path)
        self.setPixmap(pic)

class NhentaiSettings(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.save_directory = os.getcwd()
        self.log_directory = os.getcwd()
        self.directory = self.save_directory
        self.overwrite = False
        self.download = True
        self.torrent = False
        self.remove_after = False
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
        
        #self.settings = settings
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
        self.download_threads.setValue(settings.threads)
        self.delay.setValue(settings.delay)
        self.retry.setValue(settings.retry)
        self.download_image_checkbox.setChecked(settings.download)
        self.overwrite_checkbox.setChecked(settings.overwrite)
        self.download_torrent_checkbox.setChecked(settings.torrent)
        self.remove_after_checkbox.setChecked(settings.remove_after)
        self.download_end_choice.setCurrentIndex(settings.after_download.value - 1)
        self.username.setText(settings.login)
        self.password.setText(settings.password)
        
        
        
        
        
        
    def apply_settings(self):
        new_settings = NhentaiSettings()
        new_settings.save_directory = self.location_save_config_dialog.text()
        new_settings.log_directory = self.location_log_config_dialog.text()
        new_settings.threads = self.download_threads.value()
        new_settings.delay = self.delay.value()
        new_settings.retry = self.retry.value()
        new_settings.download = self.download_image_checkbox.isChecked()
        new_settings.overwrite =  self.overwrite_checkbox.isChecked()
        new_settings.torrent = self.download_torrent_checkbox.isChecked()
        new_settings.remove_after = self.remove_after_checkbox.isChecked()
        new_settings.after_download = AFTER_DOWNLOAD(self.download_end_choice.currentIndex()+1)
        new_settings.login = self.username.text()
        new_settings.password = self.password.text()
        
        self.settingsChanged.emit(new_settings)
    
    def default_settings(self):
        self.initial_config(NhentaiSettings())
    
    def open_help(self):
        webbrowser.open("https://gitlab.com/DukeValentine/nhentai-downloader/issues")
        
        
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
    



def change_thumbnail_page(stacked_widget, num):
    stacked_widget.setCurrentIndex(stacked_widget.currentIndex() + num)
    
    

class ThumbnailTable(QTableWidget):
    
    
    def __init__(self, parent = None):
        QTableWidget.__init__(self,5,5,parent)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.populate()
        
    def populate(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                self.add_widget(row,column, DoujinshiThumbnail("/home/nelarus-pc/Pictures/photos.png"))
                
        
    def add_widget(self,row,column,widget):
        self.setCellWidget(row,column,widget)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        


        
class ImgWidget2(QWidget):

    def __init__(self, path,parent=None):
        super(ImgWidget2, self).__init__(parent)
        self.pic = QPixmap(path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pic)


class MyWindowClass(QMainWindow, form_class):

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.tag_dialog = None
        self.settings = NhentaiSettings()
        self.config_dialog = None
        
        self.location_directory.setText(self.settings.save_directory)
        
    
        self.next_thumbpage.clicked.connect(lambda :change_thumbnail_page(self.thumbnail_pages,1) )
        self.previous_thumbpage.clicked.connect(lambda :change_thumbnail_page(self.thumbnail_pages,-1) )
        self.location_selection.clicked.connect(self.location_selection_click)
        self.select_tags_button.clicked.connect(self.tags_selection_click)
        self.login_button.clicked.connect(login_action)
        
        
        
        
       
        
        
        
        self.actionSettings.triggered.connect(self.settings_click)
        
        
        
        
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                self.tableWidget.resizeRowsToContents()
                self.tableWidget.resizeColumnsToContents()
                self.tableWidget.setCellWidget(row,column, DoujinshiThumbnail("/home/nelarus-pc/Pictures/photos.png"))
                
                
        
        
        
        for index in range(2,6):
           
            page_widget = QWidget()
            page_widget.setObjectName(f"page_{index}")
            grid_layout = QGridLayout(page_widget)
            
            table = ThumbnailTable(page_widget)
            grid_layout.addWidget(table,0,0,1,1)
            self.thumbnail_pages.addWidget(page_widget)
        
        
        
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
         
        if(self.tag_dialog):
            self.tag_dialog.close()
            
        if(self.config_dialog):
            self.config_dialog.close()
            
        event.accept()
        
    def search_type_change(self):
        print(f"now it's {self.search_type_selection.currentIndex()}")
        self.search_type.setCurrentIndex(self.search_type_selection.currentIndex())
        if(self.search_type_selection.currentIndex() > 0):
            self.search_type.setCurrentIndex(1)
            
        else:
            self.search_type.setCurrentIndex(0)
        
    
    def settings_click(self):
        self.config_dialog = ConfigDialog(None,self.settings)
        self.config_dialog.settingsChanged.connect(self.update_settings)
        self.config_dialog.show()
        self.config_dialog.exec_()
        
    def update_settings(self,new_settings):
        self.settings = new_settings
        self.location_directory.setText(self.settings.save_directory)
        
        
        
        
        
    def tags_selection_click(self):
        print("tags selection")
        self.tag_dialog = TagDialog(None)
        self.tag_dialog.accepted.connect(self.get_tags)
        self.tag_dialog.show()
        self.tag_dialog.exec_()
        
    def get_tags(self):
        selected_tags = " ".join(self.tag_dialog.retrieve_checked_cells())
        self.search_query_content.setText(selected_tags)
        self.tag_dialog.deleteLater()
        self.tag_dialog = None
        
    def location_selection_click(self):

        options = QFileDialog.Options()

        directory = QFileDialog.getExistingDirectory(self,"Select save location", "", options=QFileDialog.ShowDirsOnly)

        self.location_directory.setText(directory)
        self.settings.save_directory = directory
        
        
            

            
app = QApplication(sys.argv)

ThemeAction.App = app

myWindow = MyWindowClass(None)

myWindow.show()

sys.exit(app.exec_())
