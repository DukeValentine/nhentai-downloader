from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic


page_jump_class = uic.loadUiType("page_jump.ui")[0]


class PageJumpDialog(QDialog, page_jump_class):
    get_selected_page = pyqtSignal(int)
    
    
    
    def __init__(self, min_value,max_value,parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.max_value = max_value
        self.min_value = min_value
        self.spinBox.setMinimum(self.min_value)
        self.spinBox.setMaximum(self.max_value)
        
        self.label.setText(f"Jump to page : {self.min_value} - {self.max_value}")
        
        self.accepted.connect(self.send_page)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
    def execute(self):
        self.show()
        self.exec_()
        
    def send_page(self):
        self.get_selected_page.emit(self.spinBox.value())
        
    
        