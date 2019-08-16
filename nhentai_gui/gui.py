from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess, QUrl,QRunnable,QThreadPool,QThread
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
from PyQt5 import QtNetwork
import sys
from platform import system
from PyQt5 import uic
import requests
import os
import webbrowser
from enum import Enum

from config_dialog import NhentaiSettings
from config_dialog import ConfigDialog


from download_gui import ProgressBar,Worker
from main_dialogs import PageJumpDialog
from tag_dialog import TagDialog
from theme import ThemeAction
from thumbnails import ThumbnailPages

from nhentai_downloader import download
from nhentai_downloader.doujinshi import Doujinshi
from nhentai_downloader.fetcher import get_doujinshi_data
from nhentai_downloader.logger import logger,logger_config





form_class = uic.loadUiType("nhentai-downloader.ui")[0]
        



def login_action():
    print("login")
    

class DownloadWorker(QThread):
    download_finished = pyqtSignal(object)
    
    
    def __init__(self,url,path):
        super(DownloadWorker, self).__init__()
        self.url = url
    
   
    def run(self):
        print(f"run {self.url}")
        
        request = requests.get(self.url,stream = True)
        self.download_finished.emit(request)
        
        

        
        
        

class MyWindowClass(QMainWindow, form_class):
    def setup_progress_info(self):
        self.fetch_label = QLabel(self.progress_info)
        self.fetch_label.setText("Fetching doujinshi")
        self.fetch_bar = ProgressBar(self.progress_info,label=self.fetch_label)
        
        
        self.page_download_label = QLabel(self.progress_info)
        self.page_download_bar = ProgressBar(self.progress_info,label=self.page_download_label)
        
        self.doujinshi_download_label = QLabel(self.progress_info)
        self.doujinshi_download_label.setText("Downloading doujinshi id xxxx")
        self.doujinshi_download_bar = ProgressBar(self.progress_info,label= self.doujinshi_download_label)
        return
    
    

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setup_progress_info()
        self.thumbnail_pages = ThumbnailPages(self.middle_frame)
        self.grid_layout5 = QGridLayout(self.middle_frame)
        self.grid_layout5.setObjectName("gridLayout_5")
        self.grid_layout5.addWidget(self.thumbnail_pages, 0, 0, 1, 1)
        
        
        self.tag_dialog = None
        self.settings = NhentaiSettings()
        self.config_dialog = None
        
        self.location_directory.setText(self.settings.save_directory)
        
        
        self.next_thumbpage.clicked.connect(lambda :self.thumbnail_pages.switch_page(1) )
        self.previous_thumbpage.clicked.connect(lambda :self.thumbnail_pages.switch_page(-1) )
        self.page_jump_button.clicked.connect(self.page_jump_dialog)
        
        self.location_selection.clicked.connect(self.location_selection_click)
        self.select_tags_button.clicked.connect(self.tags_selection_click)
        self.login_button.clicked.connect(login_action)
        
        
        #response = requests.get("https://t.nhentai.net/galleries/1463132/thumb.jpg", stream=True)
        #print(response.status_code)
        #qimg = QImage.fromData(response.content)
        #pic = QPixmap()
        #pic.fromImage(qimg)
        
       
        url = "https://t.nhentai.net/galleries/1463132/thumb.jpg"
        request = QtNetwork.QNetworkRequest(QUrl(url))
        self.net = QtNetwork.QNetworkAccessManager()
        self.net.finished.connect(self.handle_response)
        self.net.get(request)
        
        
        self.actionSettings.triggered.connect(self.settings_click)
        
      
        
        
        
        #for row in range(self.tableWidget.rowCount()):
            #for column in range(self.tableWidget.columnCount()):
                #self.tableWidget.resizeRowsToContents()
                #self.tableWidget.resizeColumnsToContents()
                ##pic "/home/nelarus-pc/Pictures/photos.png"
                #self.tableWidget.setCellWidget(row,column, DoujinshiThumbnail(pic))
                
                
        self.tables = []
        
        
        for index in range(2,6):
            self.thumbnail_pages.create_page()
        
        
        
        available_styles_group = QActionGroup(self)
        available_styles_group.setExclusive(True)
        
        for style in QStyleFactory.keys():
            action = ThemeAction(style,self)
            available_styles_group.addAction(action)
            
        available_styles_group.addAction(ThemeAction("NhentaiDark",self))
        
        self.search_type_selection.currentIndexChanged.connect(self.search_type_change)
        
        
        self.menuAppearance.addActions(available_styles_group.actions())
        
        self.workers = []
        self.counter = 0
        
    
    def updatev(self,increment,progress_bar):
        progress_bar.setValue(progress_bar.value()+increment)
        #progress_bar.setFormat(f"{progress_bar.minimum()} of {progress_bar.maximum()}")
        
    def maximum(self,value,progress_bar):
        progress_bar.setMaximum(value)
        
    def update_label(self,text,label):
        label.setText(text)
        
    
    def multithread(self):
        base_url = "https://i.nhentai.net/galleries/1463011/"
        self.workers = []
        
        self.doujinshi_download_bar.set_maximum_value.connect(self.maximum)
        self.doujinshi_download_bar.update_value.connect(self.updatev)
        self.doujinshi_download_bar.set_label.connect(self.update_label)
        
        #progress_bar = pbar(self.doujinshi_download_bar)
        #progress_bar.update_value.connect(self.updatev)
        #progress_bar.set_maximum_value.connect(self.maximum)
        
        doujinshi = get_doujinshi_data("280762",1,5)
        worker = Worker(download.image_pool_manager,self.settings,doujinshi,self.doujinshi_download_bar)
        worker.finished.connect(self.done)
        self.workers.append(worker)
        
        
        
        worker.start()
        #download.image_pool_manager(None,self.settings,doujinshi)
        
        
        #for num in range(1,4):
            #worker = DownloadWorker(f"{base_url}{num}.jpg")
            #worker.download_finished.connect(self.down)
            #self.workers.append(worker)
            #worker.start()
            
    
    def down(self, data):
        self.counter+=1
        print(f"downloading {self.counter}")
        
        with open(f"{self.counter}",'wb') as file:
            file.write(data.content)
            
        print("done")
        
    def done(self):
        print("done")
            
    def print_output(self, s):
        print(s)
        
        
    
        
    def handle_response(self,reply):
        
        if(reply.error() != QtNetwork.QNetworkReply.NoError):
            print(f"error{reply.errorString()}")
            
        else:
            
            data = reply.readAll()
            
            
            
            self.populate_all_pages(data)
            
            reply.deleteLater()
            
        
        
        
        return
        
    
    def populate_all_pages(self,pic):
        #response = requests.get("https://t.nhentai.net/galleries/1463132/thumb.jpg", stream=True)
        #print(response.status_code)
        #qimg = QImage.fromData(response.content)
        #pic = QPixmap(qimg)
        
        
        for key,table in self.thumbnail_pages.pages.items():
            if(key%2):
                table.populate(pic)
            
        
        
        return
    
        
    def closeEvent(self, event):
        if(self.tag_dialog):
            self.tag_dialog.close()
            
        if(self.config_dialog):
            self.config_dialog.close()
            
        event.accept()
        
    def page_jump_dialog(self):
        page_jump_dialog = PageJumpDialog(1,len(self.thumbnail_pages.pages.keys()))
        page_jump_dialog.get_selected_page.connect(self.switch_page)
        page_jump_dialog.execute()
        
    def switch_page(self,page):
        print(page)
        self.thumbnail_pages.setCurrentIndex(page)
        
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
        self.config_dialog.execute()
        
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

#myWindow.multithread()

sys.exit(app.exec_())
