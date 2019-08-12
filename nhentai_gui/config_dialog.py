from PyQt5.QtCore import Qt , pyqtSlot,pyqtSignal,QObject, QProcess
from PyQt5.QtGui import QPalette, QColor,QPixmap,QPainter,QImage
from PyQt5.QtWidgets import *
import sys
from platform import system
from PyQt5 import uic
import requests
import os
import webbrowser
from enum import Enum


settings_dialog_class = uic.loadUiType("config_dialog.ui")[0]


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
