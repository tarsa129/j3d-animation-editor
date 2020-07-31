
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt, QRect

from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QSplitter, 
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QGridLayout, QMenuBar, QMenu, QAction, QApplication, QStatusBar, QLineEdit,
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem)

from PyQt5.QtGui import QMouseEvent, QImage
import PyQt5.QtGui as QtGui

import animations.general_animation as j3d


list_of_animations = []

class GenEditor(QMainWindow):
    def __init__(self):
        super().__init__()
 
        self.setup_ui()


    def setup_ui(self):
        self.resize(2500, 1000)
        self.resize_mw=QAction()
        
        
        self.setWindowTitle("j3d animation editor")
        self.setup_ui_menubar()
        
   
        
        self.show()

    def setup_ui_menubar(self):
        
        #file stuff
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 200, 50))
        self.menubar.setObjectName("menubar")
        
        #file menu
        self.file_menu = QMenu(self)
        self.file_menu.setTitle("File")

        save_file_shortcut = QtWidgets.QShortcut(Qt.CTRL + Qt.Key_S, self.file_menu)


        self.file_load_action = QAction("Load", self)
        self.save_file_action = QAction("Save", self)
        self.save_file_as_action = QAction("Save As", self)

        self.save_file_action.setShortcut("Ctrl+S")
        self.file_load_action.setShortcut("Ctrl+O")
        self.save_file_as_action.setShortcut("Ctrl+Alt+S")

        self.file_load_action.triggered.connect(self.button_load_level)
        self.save_file_action.triggered.connect(self.button_save_level)

        self.file_menu.addAction(self.file_load_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action)   
        
        self.menubar.addAction(self.file_menu.menuAction())
        self.setMenuBar(self.menubar)
        
        #left sidebar
        
        self.horizontalLayout = QSplitter()
        self.centralwidget = self.horizontalLayout
        self.setCentralWidget(self.horizontalLayout)
        
        self.animation_bar = QTreeWidget(self)
        
        self.animation_bar.setColumnCount(1)
        self.animation_bar.setHeaderLabel("animations")
        self.animation_bar.setGeometry(0, 50, 200, 850)
        self.animation_bar.resize(800, self.height())
        
        self.animation_bar.itemSelectionChanged.connect(self.selected_animation_changed) 
        
        #middle table
        
        self.table_display = QTableWidget(self)
        self.table_display.resize(1600, self.height())
        self.table_display.setColumnCount(4)
        self.table_display.setRowCount(4)
        self.table_display.setGeometry(400, 50, self.width(), self.height())
        
        self.table_display.currentItemChanged.connect(self.display_info_changes)
        
        #bottom bar
        
        self.workaround = QWidget(self)
        self.bottom_actions = QVBoxLayout(self.workaround)
        self.workaround.setGeometry(50, 50, 50, 50)
        #self.bottom_actions.setGeometry(QRect(800, 0, self.width(), self.height()) )    
        
        
        self.bt_add_col = QPushButton(self)
        self.bt_add_col.setText("Add Column")
        self.bt_add_col.clicked.connect(self.add_column)
        
        self.bt_add_row = QPushButton(self)
        self.bt_add_row.setText("Add Row")
        self.bt_add_row.clicked.connect(self.add_row)
        
        self.bt_rm_col = QPushButton(self)
        self.bt_rm_col.setText("Remove Column")
        self.bt_rm_col.clicked.connect(self.rem_column)
        
        self.bt_rm_row= QPushButton(self)
        self.bt_rm_row.setText("Remove Row")
        self.bt_rm_row.clicked.connect(self.rem_row)
        
        self.bottom_actions.addWidget(self.bt_add_col)
        self.bottom_actions.addWidget(self.bt_add_row)
        self.bottom_actions.addWidget(self.bt_rm_col)
        self.bottom_actions.addWidget(self.bt_rm_row)
        
        self.horizontalLayout.addWidget(self.animation_bar)
        self.horizontalLayout.addWidget(self.workaround)
        self.horizontalLayout.addWidget(self.table_display)     
       
    def button_load_level(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,".btk files (*.btk);;.btp files (*.btp)")
            

        if filepath:
            actual_animation_object = j3d.sort_file(filepath)
            
            new_anim = all_anim_information(filepath)           
            new_anim.display_info = actual_animation_object.get_loading_information()
            
            list_of_animations.append(new_anim)            
            loaded_animation = QTreeWidgetItem(self.animation_bar)
            
            filename = filepath[filepath.rfind("/") + 1:]
            
            loaded_animation.setText(0, filename)
            for name in actual_animation_object.get_children_names():
                child = QTreeWidgetItem(loaded_animation)
                child.setText(0, name)
                child.setDisabled(True)
            self.animation_bar.addTopLevelItem(loaded_animation)
          
            self.load_animation_to_middle(len(list_of_animations) - 1)

            
    def load_animation_to_middle(self, index):
        information = list_of_animations[index].display_info;
        col_count = max( len(information[1]), len(information[0]) )
        self.table_display.setColumnCount(col_count)
        self.table_display.setRowCount(len(information))
        
        for row in range(len(information)):
            for col in range(col_count):
                try:
                    self.table_display.setItem(row, col, QTableWidgetItem( str(information[row][col]) ))
                except:
                    pass
    
    def selected_animation_changed(self):
        index = self.animation_bar.currentIndex().row()
        #print(index)
        
        self.load_animation_to_middle(index)
        
                
    def display_info_changes(self):
        index = self.animation_bar.currentIndex().row()
        collected_info = []
        
        for i in range( self.table_display.rowCount() ):
            row_info = []
            for j in range (self.table_display.columnCount() ):
                item = self.table_display.item(i, j)
                if isinstance(item, QTableWidgetItem):
                    row_info.append(item.text())
                    #print(item.text())
                else:
                    row_info.append("")
            collected_info.append(row_info)
        #print(collected_info)
        list_of_animations[index].display_info = collected_info
                
        
    def button_save_level(self):
        index = self.animation_bar.currentIndex().row()
        
        j3d.sort_filepath(list_of_animations[index].filepath, list_of_animations[index].display_info) 
   
    def add_column(self):
        self.table_display.setColumnCount(self.table_display.columnCount() + 1)
        
    def rem_column(self):
        self.table_display.setColumnCount(self.table_display.columnCount() - 1)
        
    def add_row(self):
        self.table_display.setRowCount(self.table_display.rowCount() + 1)
    
    def rem_row(self):
        self.table_display.setRowCount(self.table_display.rowCount() - 1)
                    
import sys
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

class all_anim_information(object):
    def __init__(self, filepath, current_array = []):
        self.filepath = filepath
        self.display_info = current_array

if __name__ == "__main__":
    #import sys
    import platform
    import argparse
    from PyQt5.QtCore import QLocale

    QLocale.setDefault(QLocale(QLocale.English))
    sys.excepthook = except_hook

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputgen", default=None,
                        help="Path to generator file to be loaded.")
    parser.add_argument("--collision", default=None,
                        help="Path to collision to be loaded.")
    parser.add_argument("--waterbox", default=None,
                        help="Path to waterbox file to be loaded.")

    args = parser.parse_args()

    app = QApplication(sys.argv)

    pikmin_gui = GenEditor()
    pikmin_gui.show()
    
    err_code = app.exec()

    sys.exit(err_code)
