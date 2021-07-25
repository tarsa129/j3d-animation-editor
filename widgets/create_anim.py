import os
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt, QRect, QModelIndex

from PyQt5.QtWidgets import (QWidget, QDialog, QFileDialog, QSplitter, QListWidget, QListWidgetItem,
                             QScrollArea, QGridLayout, QAction, QApplication, QStatusBar, QLineEdit,
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout)

from PyQt5.QtGui import QMouseEvent, QImage
import PyQt5.QtGui as QtGui

class create_window(QDialog):
    def __init__(self):
        super().__init__()
 
        
        
        self.file_types_names = {".btk", ".brk", ".bck" , ".btp", ".bca", ".bpk", ".bla", ".blk" };
        
        #stuff that we want to return / have access to
        self.selected = None
        self.filepath = None
        
        self.setup_ui()
        
    
    def setup_ui(self):
        self.resize(800, 400)
        self.resize_mw=QAction()
        self.setWindowTitle("create j3d animation")
        
        self.horizontalLayout = QHBoxLayout()
        self.centralwidget = self.horizontalLayout
        #self.setCentralWidget(self.horizontalLayout)
        
        self.setLayout(self.centralwidget)
        
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
        self.other_info_layout.setGeometry(0, 0, 250, 250)
        self.other_info_box = QGridLayout(self.other_info_layout)
        
        self.filename_label = QLabel(self.other_info_layout)
        self.filename_label.setText("Filename")
        self.filename_text = QLineEdit(self.other_info_layout)
        self.filename_button = QPushButton("Set Name")  
        self.filename_button.setDisabled(True)   
        self.filename_button.clicked.connect(self.open_file_dialog)
            
        self.number_label = QLabel(self.other_info_layout)
        self.number_label.setText(self.get_text())
        self.number_text = QLineEdit(self.other_info_layout)
        self.number_text.setDisabled(True)
        
        self.const_label = QLabel(self.other_info_layout)
        self.const_label.setText("Number of Constant Materials")
        self.const_label.setDisabled(True)
        self.const_text = QLineEdit(self.other_info_layout)
        self.const_text.setDisabled(True)
        
        self.duration_label = QLabel(self.other_info_layout)
        self.duration_label.setText("Duration")
        self.duration_text = QLineEdit(self.other_info_layout)  

        self.close_button = QPushButton(self.other_info_layout)
        self.close_button.setText("Create")
        self.close_button.clicked.connect(self.close_window)
        
        self.other_info_box.addWidget(self.filename_label, 0, 0)
        self.other_info_box.addWidget(self.filename_text, 0, 1)
        self.other_info_box.addWidget(self.filename_button, 1, 1)
        self.other_info_box.addWidget(self.number_label, 2, 0)
        self.other_info_box.addWidget(self.number_text, 2, 1)
        self.other_info_box.addWidget(self.const_label, 3, 0)
        self.other_info_box.addWidget(self.const_text, 3, 1)
        self.other_info_box.addWidget(self.duration_label, 4, 0)
        self.other_info_box.addWidget(self.duration_text, 4, 1)
        self.other_info_box.addWidget(self.close_button, 5, 0)
        
        
        self.horizontalLayout.addWidget(self.type_layout)
        self.horizontalLayout.addWidget(self.other_info_layout)
        
    
    def setup_list_box(self):
        self.file_types.clear()
        for type in self.file_types_names:
            self.file_types.addItem(type)
        self.file_types.clicked.connect(self.set_selected)
        
    def set_selected(self):
        self.selected = self.file_types.currentItem().text()
        self.number_label.setText(self.get_text())
    
    def get_text(self):
        if self.selected is not None:
            self.number_text.setDisabled(False)
            self.filename_button.setDisabled(False)
            if self.selected == ".bck" or self.selected == ".bca":
                self.const_label.setDisabled(True)
                self.const_text.setDisabled(True)
                return "Number of Bones"
            elif self.selected == ".brk":
                self.const_label.setDisabled(False)
                self.const_text.setDisabled(False)
                return "Number of Register Materials"
            elif self.selected == ".bla" or self.selected == ".blk":
                self.const_label.setDisabled(True)
                self.const_text.setDisabled(True)
                return "Number of Clusters"
            else:
                self.const_label.setDisabled(True)
                self.const_text.setDisabled(True)
                return "Number of Materials"
        else:
            return "Choose an animation type"

    def get_info(self):
        if self.selected is None:
            return None
        if not self.number_text.text().isnumeric() or not self.duration_text.text().isnumeric():
            return None
        if self.selected == ".brk" and not self.const_text.text().isnumeric():
            return None
        if self.filepath is None and self.filename_text.text() == "":
            return None
        elif self.filepath is None and self.filename_text.text() != "":
            print("textbox has something")
            self.filepath = os.getcwd() + "/" + self.filename_text.text() + self.selected
        print(self.filepath)
        return (self.filepath, self.number_text.text(), self.const_text.text(), self.duration_text.text() )
         
    def open_file_dialog(self):
        filepath, choosentype = QFileDialog.getOpenFileName(self.other_info_layout, "Choose File Path", "", self.selected + " files (*" + self.selected + ")")
        if filepath:
            self.filename_text.setText(filepath)
            self.filepath = filepath
    def close_window(self):
        self.close()