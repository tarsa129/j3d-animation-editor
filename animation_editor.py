
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
        self.save_file_as_action.triggered.connect(self.button_save_as)

        self.file_menu.addAction(self.file_load_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action)   
        
        self.menubar.addAction(self.file_menu.menuAction())
        self.setMenuBar(self.menubar)
        
        
        #convert menu
        self.convert = QMenu(self)
        self.convert.setTitle("Convert")
        
        self.convert_to_key = QAction("Save as Keyframes", self)
        self.convert_to_all = QAction("Convert to All", self)
        
        self.convert_to_key.triggered.connect(self.convert_to_k)
        self.convert_to_all.triggered.connect(self.convert_to_a)
        
        self.convert.addAction(self.convert_to_key)
        self.convert.addAction(self.convert_to_all)
        
        self.convert.setDisabled(True)
        
        self.menubar.addAction(self.convert.menuAction())
        
        #main splitter
        
        self.horizontalLayout = QSplitter()
        self.centralwidget = self.horizontalLayout
        self.setCentralWidget(self.horizontalLayout)
        
        #left sidebar
        self.workaroundl = QWidget(self)
        self.left_vbox = QVBoxLayout(self.workaroundl)
        
        #tree view
        
        self.animation_bar = QTreeWidget(self.workaroundl)       
        self.animation_bar.setColumnCount(1)
        self.animation_bar.setHeaderLabel("animations")
        self.animation_bar.setGeometry(0, 50, 200, 850)
        self.animation_bar.resize(800, self.height())
        
        self.animation_bar.itemSelectionChanged.connect(self.selected_animation_changed) 
        
        #self.animation_bar.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.animation_bar.customContextMenuRequested.connect(self.run_context_menu)
        
        self.left_vbox.addWidget(self.animation_bar)
        
        #middle table
        
        self.table_display = QTableWidget(self)
        self.table_display.resize(1600, self.height())
        self.table_display.setColumnCount(4)
        self.table_display.setRowCount(4)
        self.table_display.setGeometry(400, 50, self.width(), self.height())
        
        self.table_display.currentItemChanged.connect(self.display_info_changes)
        
        #bottom bar
        
        self.workaround = QWidget(self)
        self.bottom_actions = QGridLayout(self.workaround)
        self.workaround.setGeometry(50, 50, 50, 50)
        #self.bottom_actions.setGeometry(QRect(800, 0, self.width(), self.height()) )            
        
        self.bt_addc_here = QPushButton(self)
        self.bt_addc_here.setText("Add Column Next")
        self.bt_addc_here.clicked.connect(self.add_col_here)
        
        self.bt_add_col = QPushButton(self)
        self.bt_add_col.setText("Add Column To End")
        self.bt_add_col.clicked.connect(self.add_column)
        
        self.bt_remc_here = QPushButton(self)
        self.bt_remc_here.setText("Rem. Current Column")
        self.bt_remc_here.clicked.connect(self.rem_col_here)
        
        self.bt_rm_col = QPushButton(self)
        self.bt_rm_col.setText("Remove Column")
        self.bt_rm_col.clicked.connect(self.rem_column)
        
        self.bt_add_row = QPushButton(self)
        self.bt_add_row.setText("Add Row To End")
        self.bt_add_row.clicked.connect(self.add_row)
        
        self.bt_addr_here = QPushButton(self)
        self.bt_addr_here.setText("Add Row Next")
        self.bt_addr_here.clicked.connect(self.add_row_here)  
             
        self.bt_rm_row = QPushButton(self)
        self.bt_rm_row.setText("Remove Row")
        self.bt_rm_row.clicked.connect(self.rem_row) 

        self.bt_remr_here = QPushButton(self)
        self.bt_remr_here.setText("Rem. Current Row")
        self.bt_remr_here.clicked.connect(self.rem_row_here)        
        
        self.bottom_actions.addWidget(self.bt_addc_here, 0, 0)       
        self.bottom_actions.addWidget(self.bt_addr_here, 0, 1)
        self.bottom_actions.addWidget(self.bt_add_col, 1 ,0)
        self.bottom_actions.addWidget(self.bt_add_row, 1, 1)
        self.bottom_actions.addWidget(self.bt_remc_here, 2, 0)
        self.bottom_actions.addWidget(self.bt_remr_here, 2, 1)
        self.bottom_actions.addWidget(self.bt_rm_col, 3, 0)
        self.bottom_actions.addWidget(self.bt_rm_row, 3, 1)
               
        self.left_vbox.addWidget(self.workaround)
        
        #self.horizontalLayout.addWidget(self.animation_bar)
        self.horizontalLayout.addWidget(self.workaroundl)
        self.horizontalLayout.addWidget(self.table_display)     
    
    #file stuff
      
    def button_load_level(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,
        "All Files(*.*);;.bck files (*.bck);;.brk files (*.brk);;.btk files (*.btk);;.btp files (*.btp)"
        )
            

        if filepath:
        
            self.convert.setDisabled(False)
            
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

    def button_save_level(self):
        index = self.animation_bar.currentIndex().row()      

        info = j3d.fix_array(list_of_animations[index].display_info)
  
        j3d.sort_filepath(list_of_animations[index].filepath, info) 
    
    def button_save_as(self): 
        filepath, choosentype = QFileDialog.getSaveFileName(self, "Save File", "", ".brk files (*.brk);;.btk files (*.btk);;.btp files (*.btp);;All files (*)")
        if filepath:
            info = j3d.fix_array(list_of_animations[index].display_info)
            j3d.sort_filepath(filepath, info) 
       
    #convert stuff

    def convert_to_k(self):
        index = self.animation_bar.currentIndex().row()
        filepath = list_of_animations[index].filepath
        
        if filepath.endswith(".bca"):
            filepath = filepath[:-1] + "k"
            info = list_of_animations[index].display_info           
            bck = j3d.sort_filepath(filepath, info)
        
    def convert_to_a(self):
        index = self.animation_bar.currentIndex().row()
        filepath = list_of_animations[index].filepath
        
        if filepath.endswith(".bck"):
            info = list_of_animations[index].display_info
         
            bck = j3d.convert_to_k(filepath, info) #this is a pure bck, no saving
            filepath = filepath[:-1] + "a"
                       
        
    #tree view stuff
    def contextMenuEvent(self, event):
        
        if len( list_of_animations ) < 1:
            return
        
        if len( list_of_animations) == 1:
            self.convert.setDisabled(True)
        
        index = self.animation_bar.currentIndex().row()
        
        #print("context menu triggered")
        
        context_menu = QMenu(self.animation_bar)
        close_action = QAction("Close", self)
        copy_action = QAction("Copy", self)
        
        def emit_close():
            items = self.animation_bar.selectedItems()
            
            if ( len(items) > 1):
                return
            
            self.animation_bar.takeTopLevelItem(index)
            list_of_animations.pop(index)
            
            print( len (list_of_animations ))
            
        def emit_copy():
            items = self.animation_bar.selectedItems()
            
            if ( len(items) > 1):
                return
            
            current_entry = list_of_animations[index]
            copied_entry = all_anim_information.get_copy(current_entry)
            list_of_animations.insert(index + 1, copied_entry)
            
            #print( len( list_of_animations) )
            
            
            
            widget = self.animation_bar.selectedItems()
            widget = widget[0].clone()
            
            self.animation_bar.addTopLevelItem(widget)
            
            
        close_action.triggered.connect(emit_close)
        copy_action.triggered.connect(emit_copy)
       
        context_menu.addAction(close_action)
        context_menu.addAction(copy_action)
        context_menu.exec(self.mapToGlobal(event.pos()))
        context_menu.destroy()
        del context_menu
        
    #table info stuff
    
    def load_animation_to_middle(self, index):      
        information = list_of_animations[index].display_info;
        
        self.table_display.setColumnCount(0)
        self.table_display.setRowCount(0)
        
        col_count = 1
        for i in range(len (information)):
            col_count = max(col_count, len( information [i] ) )
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
        print(index)
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
                
    #table button stuff   
   
    def add_column(self):
        self.table_display.setColumnCount(self.table_display.columnCount() + 1)
        if len(list_of_animations) > 0:
            index = self.animation_bar.currentIndex().row()
            minimum = len (list_of_animations[index].display_info[0] )
            if self.table_display.columnCount() > minimum:
                self.bt_rm_col.setDisabled(False)
        
    def rem_column(self):
        if len(list_of_animations) > 0:
            index = self.animation_bar.currentIndex().row()
            vals = list_of_animations[index].display_info[0]
            
            minimum = 0;
            
            for i in vals:
                if i != "":
                    minimum += 1
            if self.table_display.columnCount() > minimum:
                self.table_display.setColumnCount(self.table_display.columnCount() - 1)
        else:
            self.table_display.setColumnCount(self.table_display.columnCount() - 1)
    
    def add_col_here(self):
        curcol = self.table_display.currentColumn() + 2
        #print(self.table_display.currentColumn())
        self.add_column()
        if curcol > 2:
            #print("at least 2")
            for i in range( 1, self.table_display.rowCount() ):
                for j in reversed( range( curcol, self.table_display.columnCount() ) ):
                    old = self.table_display.item(i, j-1)
                    try:
                        new = QTableWidgetItem(old.text())
                        old.setText("")
                    except:
                        new = QTableWidgetItem("")
                        self.table_display.setItem(i, j-1, QTableWidgetItem(""))
                    self.table_display.setItem(i, j, new)
    
    def rem_col_here(self):
        curcol = self.table_display.currentColumn() + 1
        print(curcol)
        if len(list_of_animations) > 0:          
            index = self.animation_bar.currentIndex().row()
            vals = list_of_animations[index].display_info[0]
            
            minimum = 0;
            
            for i in vals:
                if i != "":
                    minimum += 1
            
            print(minimum)
            
            print("removing column")
            for i in range( 1, self.table_display.rowCount() ):
                for j in range( curcol, self.table_display.columnCount() ):
                    old = self.table_display.item(i, j)
                    try:
                        new = QTableWidgetItem(old.text())
                        old.setText("")
                    except:
                        new = QTableWidgetItem("")
                        self.table_display.setItem(i, j, QTableWidgetItem(""))
                    self.table_display.setItem(i, j - 1, new)
            
            
            if self.table_display.columnCount() > minimum: #if you can remove a col            
                self.rem_column()
        else:
            self.rem_column()
    
    def add_row(self):
        self.table_display.setRowCount(self.table_display.rowCount() + 1)
        if self.table_display.rowCount() > 2:
            self.bt_rm_row.setDisabled(False)
    
    def rem_row(self):
        if self.table_display.rowCount() > 2:
            self.table_display.setRowCount(self.table_display.rowCount() - 1)
        if self.table_display.rowCount() == 2:
            self.bt_rm_row.setDisabled(True)
    
    def add_row_here(self):
        currow = self.table_display.currentRow() + 2
        print(self.table_display.currentRow())
        self.add_row()
        if currow > 2:
            for i in reversed( range( currow, self.table_display.rowCount() ) ):
                for j in range( 0, self.table_display.columnCount() ):
                    old = self.table_display.item(i - 1, j)
                    try:
                        new = QTableWidgetItem(old.text())
                        old.setText("")
                    except:
                        new = QTableWidgetItem("")
                        self.table_display.setItem(i - 1, j, QTableWidgetItem(""))
                    self.table_display.setItem(i, j, new)
    
    def rem_row_here(self):
        currow = self.table_display.currentRow() + 2
        if currow == 0:
            self.rem_row()
        elif len(list_of_animations) > 0:          
            index = self.animation_bar.currentIndex().row()
            minimum = len (list_of_animations[index].display_info[0] )
            
            if self.table_display.rowCount() > minimum: #if you can remove a col          
                for i in range( currow, self.table_display.rowCount() ):
                    for j in range( 0, self.table_display.columnCount() ):
                        old = self.table_display.item(i, j)
                        try:
                            new = QTableWidgetItem(old.text())
                            old.setText("")
                        except:
                            new = QTableWidgetItem("")
                            self.table_display.setItem(i, j, QTableWidgetItem(""))
                        self.table_display.setItem(i - 1, j, new)
                self.rem_row()
        else:
            self.rem_row()
    
import sys
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

class all_anim_information(object):
    def __init__(self, filepath, current_array = []):
        self.filepath = filepath
        self.display_info = current_array
    
    @classmethod
    def get_copy(cls, entry):
        copy = cls(entry.filepath, entry.display_info)
        return copy

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
