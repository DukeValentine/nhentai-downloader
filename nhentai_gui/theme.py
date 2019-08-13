from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *


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
