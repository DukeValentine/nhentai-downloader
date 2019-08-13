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

from tag_dialog import TagDialog
from theme import ThemeAction

from nhentai_downloader import download
from nhentai_downloader.doujinshi import Doujinshi
from nhentai_downloader.fetcher import get_doujinshi_data
from nhentai_downloader.logger import logger,logger_config



QProcess().start()

form_class = uic.loadUiType("nhentai-downloader.ui")[0]
thumbnail_class = uic.loadUiType("doujinshi_thumbnail.ui")[0]









class DoujinshiThumbnail(QWidget,thumbnail_class):
    def __init__(self, pic,main_id = None, media_id = None ,parent=None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        pixmap = QPixmap()
        pixmap.loadFromData(pic)
        
        self.label.setPixmap( pixmap)
        self.label.show()
        
        self.main_id = main_id
        self.media_id = media_id
        
        #qimg = QImage.fromData(response.content)
        #pic = QPixmap()
        #pic.fromImage(qimg)
        
        
    def mousePressEvent(self, event):
        self.checkBox.setChecked(not self.checkBox.isChecked())
        



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
        #self.populate()
        
    def populate(self,picture):
        
        for row in range(self.rowCount()):
            for column in range(self.columnCount()): #"/home/nelarus-pc/Pictures/photos.png"
                self.add_widget(row,column, DoujinshiThumbnail(picture))
                
        
    def add_widget(self,row,column,widget):
        self.setCellWidget(row,column,widget)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        


class Worker(QThread):
    worker_finished = pyqtSignal(object)
    
    
    def __init__(self,function,options,doujinshi,pbar):
        super(Worker, self).__init__()
        self.function = function
        self.options = options
        self.doujinshi = doujinshi
        self.pbar = pbar
        
    def run(self):
        logger_config(10)
        self.function(logger,self.options , self.doujinshi,self.pbar)


class DownloadWorker(QThread):
    download_finished = pyqtSignal(object)
    
    
    def __init__(self,url,path):
        super(DownloadWorker, self).__init__()
        self.url = url
    
   
    def run(self):
        print(f"run {self.url}")
        
        request = requests.get(self.url,stream = True)
        self.download_finished.emit(request)
        
        
class pbar(QProgressBar):
    update_value = pyqtSignal(int)
    set_maximum_value = pyqtSignal(int)
    
    def __init__(self):
        QObject.__init__(self)
        
    def update_progress(self,increment):
        self.update_value.emit(increment)
        
    def setMaximum(self,value):
        self.set_maximum_value.emit(value)
        

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
           
            page_widget = QWidget()
            
            
            
            page_widget.setObjectName(f"page_{index}")
            grid_layout = QGridLayout(page_widget)
            
            table = ThumbnailTable(page_widget)
            grid_layout.addWidget(table,0,0,1,1)
            self.thumbnail_pages.addWidget(page_widget)
            
            self.tables.append(table)
        
        
        
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
        
    
    def updatev(self,increment):
        self.doujinshi_download_bar.setValue(self.doujinshi_download_bar.value()+increment)
        
    def maximum(self,value):
        self.doujinshi_download_bar.setMaximum(value)
        
    
    def multithread(self):
        base_url = "https://i.nhentai.net/galleries/1463011/"
        self.workers = []
        
        progress_bar = pbar()
        progress_bar.update_value.connect(self.updatev)
        progress_bar.set_maximum_value.connect(self.maximum)
        
        doujinshi = get_doujinshi_data("280762",1,5)
        worker = Worker(download.image_pool_manager,self.settings,doujinshi,progress_bar)
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
        
        
        for table in self.tables:
            table.populate(pic)
            
        
        
        return
    
        
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

myWindow.multithread()

sys.exit(app.exec_())
