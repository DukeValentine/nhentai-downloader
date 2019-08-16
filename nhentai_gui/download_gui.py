from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess, QUrl,QRunnable,QThreadPool,QThread
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
from nhentai_downloader.logger import logger,logger_config

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

class ProgressBar(QProgressBar):
    update_value = pyqtSignal(int,object)
    set_maximum_value = pyqtSignal(int,object)
    set_label = pyqtSignal(object,object)
    
    def __init__(self, parent = None, value = 0,max = 100, label = None):
        QProgressBar.__init__(self,parent)
        self.setValue(value)
        self.setMaximum(max)
        self.label = label
        self.setTextVisible(True)
        
    def start(self):
        pass
        
    def update_progress(self,increment):
        self.update_value.emit(increment,self)
        
    def set_maximum(self,value):
        self.set_maximum_value.emit(value,self)
        
    def get_current_progress(self):
        return self.value()/self.maximum()
        
    def setLabel(self,label):
        if(self.label):
            self.set_label.emit(label,self.label)
