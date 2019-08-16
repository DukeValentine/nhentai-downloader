from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess, QUrl,QRunnable,QThreadPool,QThread
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic


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
        
        
class ThumbnailPages(QStackedWidget):
    def __init__(self, parent = None):
        QStackedWidget.__init__(self,parent)
        self.setObjectName("thumbnail_pages")
        self.pages = dict()
        #self.pages[1] = 
        self.create_page()
        
    def switch_page(self,increment):
        self.setCurrentIndex(self.currentIndex() + increment)
        
    def create_page(self):
        index = len(self.pages.keys()) + 1
        
        page_widget = QWidget()
        page_widget.setObjectName(f"page_{index}")
        grid_layout = QGridLayout(page_widget)
        table = ThumbnailTable(page_widget)
        grid_layout.addWidget(table,0,0,1,1)
        
        self.pages[index] = table
        self.addWidget(page_widget)
        
    
    

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
