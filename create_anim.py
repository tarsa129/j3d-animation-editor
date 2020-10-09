import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt, QRect, QModelIndex

from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QSplitter, QListWidget, QListWidgetItem,
                             QScrollArea, QGridLayout, QAction, QApplication, QStatusBar, QLineEdit,
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout)

from PyQt5.QtGui import QMouseEvent, QImage
import PyQt5.QtGui as QtGui

class create_window(QMainWindow):
    def __init__(self):
        super().__init__()
 
        
        
        self.file_types_names = {".btk", ".brk", ".bck" , ".btp", ".bca", ".bpk" };
        
        #stuff that we want to return / have access to
        self.selected = None
        self.duration = None
        self.entries = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.resize(800, 200)
        self.resize_mw=QAction()
        self.setWindowTitle("create j3d animation")
        
        self.horizontalLayout = QSplitter()
        self.centralwidget = self.horizontalLayout
        self.setCentralWidget(self.horizontalLayout)
        
        #choose the animation type
        self.type_layout = QWidget(self)
        self.type_box = QVBoxLayout(self.type_layout)
        
        self.select_label = QLabel(self.type_layout)
        self.select_label.setText("Select Animation Type")
        self.file_types = QListWidget(self.type_layout)
        self.setup_list_box()
        
        self.type_box.addWidget(self.select_label)
        self.type_box.addWidget(self.file_types)
        
        #other needed info
        self.other_info_layout = QWidget(self)
        self.other_info_box = QVBoxLayout(self.other_info_layout)
            
        self.number_label = QLabel(self.other_info_layout)
        self.number_label.setText(self.get_text())
        
        
        self.horizontalLayout.addWidget(self.type_layout)
        self.horizontalLayout.addWidget(self.other_info_layout)
        self.show()
    
    def setup_list_box(self):
        self.file_types.clear()
        for type in self.file_types_names:
            self.file_types.addItem(type)
        self.file_types.doubleClicked.connect(self.set_selected)
        
    def set_selected(self):
        self.selected = self.listbox.currentItem().text()
        self.number_label.setText(self.get_text())
    
    def get_text(self):
        if self.selected is not None:
            if self.selected == ".bck" or self.selected == ".bca":
                return "Number of Bones"
            else:
                return "Number of Materials"
        else:
            return "Choose an animation type"
        