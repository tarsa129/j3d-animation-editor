
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt, QRect, QModelIndex

from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QSplitter, 
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QGridLayout, QMenuBar, QMenu, QAction, QApplication, QStatusBar, QLineEdit,
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem)

from PyQt5.QtGui import QMouseEvent, QImage
import PyQt5.QtGui as QtGui

import animations.general_animation as j3d
import create_anim as create_widget


list_of_animations = []

class GenEditor(QMainWindow):
    def __init__(self):
    
        super().__init__()
 
        self.setup_ui()
        
        self.copied_values = []
        self.current_index = 0;
        self.create_window = None
        self.is_remove = False

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
        self.create_animation = QAction("Create Animation", self)
        
        self.save_file_action.setShortcut("Ctrl+S")
        self.file_load_action.setShortcut("Ctrl+O")
        self.save_file_as_action.setShortcut("Ctrl+Alt+S")
        self.create_animation.setShortcut("Ctrl+N")

        self.file_load_action.triggered.connect(self.button_load_level)
        self.save_file_action.triggered.connect(self.button_save_level)
        self.save_file_as_action.triggered.connect(self.button_save_as)
        self.create_animation.triggered.connect(self.create_new)

        self.file_menu.addAction(self.file_load_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action)   
        self.file_menu.addAction(self.create_animation)
        
        self.menubar.addAction(self.file_menu.menuAction())
        self.setMenuBar(self.menubar)
        
        
        #edit menu
        
        self.edit_menu = QMenu(self)
        self.edit_menu.setTitle("Edit")

        self.copy_cells_action = QAction("Copy Selected Cells", self)
        self.paste_cells_action = QAction("Paste Selected Cells", self)  
        self.clear_cells_action = QAction("Clear Selected Cells", self)
        
        self.copy_cells_action.triggered.connect(self.emit_copy_cells)
        self.paste_cells_action.triggered.connect(self.emit_paste_cells)
        self.clear_cells_action.triggered.connect(self.emit_clear_cells)
        
        self.copy_cells_action.setShortcut("Ctrl+C")
        self.paste_cells_action.setShortcut("Ctrl+V")
        self.clear_cells_action.setShortcut("Delete")
        
        self.edit_menu.addAction(self.copy_cells_action)
        self.edit_menu.addAction(self.paste_cells_action)
        self.edit_menu.addAction(self.clear_cells_action)
        
        self.menubar.addAction(self.edit_menu.menuAction())
        
        #convert menu
        self.convert = QMenu(self)
        self.convert.setTitle("Convert")
        
        self.convert_to_key = QAction("Save as Keyframes", self)
        self.convert_to_all = QAction("Save as All", self)
        
        self.convert_to_key.triggered.connect(self.convert_to_k)
        self.convert_to_all.triggered.connect(self.convert_to_a)
        
        self.convert_to_key.setShortcut("Ctrl+K")
        
        self.convert.addAction(self.convert_to_key)
        self.convert.addAction(self.convert_to_all)
        
        self.convert.setDisabled(True)
        
        self.menubar.addAction(self.convert.menuAction())
        
        
        
        #load bmd
        
        self.model = QMenu(self)
        self.model.setTitle("Load .bmd")
        
        self.load_bones = QAction("Load Bone Names", self)
        self.load_bones.triggered.connect(self.load_bone_names)
        self.load_bones.setShortcut("Ctrl+L")
        
        
        self.model.addAction(self.load_bones)
       
        self.model.setDisabled(True)
        
        self.menubar.addAction(self.model.menuAction())
        
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
        
        
        
        #self.table_display.currentItemChanged.connect(self.display_info_changes)
        
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

        filepaths, choosentype = QFileDialog.getOpenFileNames( self, "Open File","" ,
        "All Files(*.*);;.bck files (*.bck);;.brk files (*.brk);;.btk files (*.btk);;.btp files (*.btp)"
        )
            
        for filepath in filepaths:
            if filepath:
                
                self.convert.setDisabled(False)

                actual_animation_object = j3d.sort_file(filepath)
                
                new_anim = all_anim_information(filepath)           
                new_anim.display_info = actual_animation_object.get_loading_information()
                
                if len( list_of_animations ) > 0:
                    print( "this is not the first loaded animation " ) 
                    index = self.animation_bar.currentIndex().row()
                    print( "the old index is " + str(index) )
                    print( list_of_animations[index].display_info[0] ) 
                    list_of_animations[index].display_info = self.get_on_screen()
                    print( list_of_animations[index].display_info[0] ) 
                
                
                list_of_animations.append(new_anim)            
                loaded_animation = QTreeWidgetItem(self.animation_bar)
                
                filename = filepath[filepath.rfind("/") + 1:]
                
                loaded_animation.setText(0, filename)
                for name in actual_animation_object.get_children_names():
                    child = QTreeWidgetItem(loaded_animation)
                    child.setText(0, name)
                    child.setDisabled(True)
                   
            self.animation_bar.addTopLevelItem(loaded_animation)       
            self.current_index = len(list_of_animations) - 1
            self.load_animation_to_middle(len(list_of_animations) - 1)
            self.animation_bar.setCurrentItem(loaded_animation)
            

    def button_save_level(self):
        index = self.animation_bar.currentIndex().row()      
        list_of_animations[index].display_info = self.get_on_screen()
        info = j3d.fix_array(list_of_animations[index].display_info)
        if (list_of_animations[index].filepath.endswith(".bca") ):
            self.convert_to_a()
        else: 
            j3d.sort_filepath(list_of_animations[index].filepath, info) 
    
    def button_save_as(self): 
        filepath, choosentype = QFileDialog.getSaveFileName(self, "Save File", "", ".brk files (*.brk);;.btk files (*.btk);;.btp files (*.btp);;All files (*)")
        if filepath:
            index = self.animation_bar.currentIndex().row()  
            list_of_animations[index].display_info = self.get_on_screen()
            info = j3d.fix_array(list_of_animations[index].display_info)
            j3d.sort_filepath(filepath, info) 
            
    def create_new(self):
        
        if self.create_window is None:
            self.create_window = create_widget.create_window()
            self.create_window.setWindowModality(QtCore.Qt.ApplicationModal)
            self.create_window.exec_()
            
        created_info = self.create_window.get_info() 
        if created_info is not None:
            table = j3d.create_empty( created_info )
            filepath = created_info[0]
            new_anim = all_anim_information(filepath, table)           
            
            if len( list_of_animations ) > 0:
                index = self.animation_bar.currentIndex().row()
                list_of_animations[index].display_info = self.get_on_screen()
            
            list_of_animations.append(new_anim)            
            loaded_animation = QTreeWidgetItem(self.animation_bar)
            
            filename = filepath[filepath.rfind("/") + 1:]
            loaded_animation.setText(0, filename)
        
            self.animation_bar.addTopLevelItem(loaded_animation)       
            self.current_index = len(list_of_animations) - 1
            self.load_animation_to_middle(len(list_of_animations) - 1)
            self.animation_bar.setCurrentItem(loaded_animation)
        
        self.create_window = None
    #convert stuff

    def convert_to_k(self):
        index = self.animation_bar.currentIndex().row()          
        list_of_animations[index].display_info = self.get_on_screen()
        
        
        filepath = list_of_animations[index].filepath
        if filepath.endswith(".bca"):
            filepath = filepath[:-1] + "k"
            info = list_of_animations[index].display_info           
            bck = j3d.sort_filepath(filepath, info)
        
    def convert_to_a(self):
        index = self.animation_bar.currentIndex().row()
        filepath = list_of_animations[index].filepath
        
        list_of_animations[index].display_info = self.get_on_screen()
        
        if filepath.endswith(".bck") or filepath.endswith(".bca"):
            info = list_of_animations[index].display_info
         
            bca = j3d.convert_to_a(filepath, info) #this is a pure bck, no saving
            filepath = filepath[:-1] + "a"
            print("new filepath is " + filepath)
            with open(filepath, "wb") as f:
            
                bca.write_bca(f)
                f.close()
      
    #bmd stuff
    def load_bone_names(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , ".bmd files(*.bmd)")
        if filepath:    
            with open(filepath, "rb") as f:
                s = f.read()
                a = s.find(b'\x4A\x4E\x54\x31')
                print(a)
                f.seek(a + 0x14);
                address = j3d.read_uint32(f)
                print(address)
                f.seek(address + a)
                strings = j3d.StringTable.from_file(f).strings;
                print(strings)
                f.close()
            #index = self.animation_bar.currentIndex().row()
            information = self.get_on_screen()
            #information = list_of_animations[index].display_info
            for i in range( len(strings) ):
                information[9*i+2][0] = strings[i]
            #list_of_animations[index].display_info = information
            self.load_animation_to_middle(0, information)
            
  
     
    #tree view stuff
    def contextMenuEvent(self, event):
        
        if len( list_of_animations ) < 1:
            return
        
        if len( list_of_animations) == 1:
            self.convert.setDisabled(True)
        
        index = self.animation_bar.currentIndex().row()
        
        #print("context menu triggered")
        
        context_menu = QMenu(self.animation_bar)
        close_action = QAction("Close Current Animation", self)
        copy_action = QAction("Copy Animation", self)
        
        
        def emit_close():
            
            print(" emit close ")
            
            self.is_remove = True

            
            items = self.animation_bar.selectedItems()         
            if ( len(items) > 1):
                return
            
            item = items[0]
            index = self.animation_bar.indexFromItem(item)
            
            index = index.row()    #index is the thing to be deleted
            print( "the index is " + str(index) )
            
            list_of_animations.pop(index) #remove from list

            if len( list_of_animations ) == 0: #if there is nothing left, simply clear and return
                self.table_display.clearContents()
                self.animation_bar.takeTopLevelItem(0)
                self.is_remove = False
                return
            else: #there are more animations - select the one below item
                self.current_index = max(index - 1, 0);
                item = self.animation_bar.itemAt(self.current_index, 0);
                
            print("remove item from the tree")
            self.animation_bar.takeTopLevelItem(index) #triggers selected_animation_changed 
            self.table_display.clearContents()  
            
            print("load the previous animation to the middle. index: " + str(index) )
            self.load_animation_to_middle(self.current_index)
            
            
            self.animation_bar.setCurrentItem(item)
            self.is_remove = False
            print("done with removing")
                            
        def emit_copy():
            items = self.animation_bar.selectedItems()
            
            if ( len(items) > 1):
                return

            current_entry = list_of_animations[index]
            copied_entry = all_anim_information.get_copy(current_entry)
            list_of_animations.insert(index + 1, copied_entry)
             
            widget = self.animation_bar.selectedItems()
            widget = widget[0].clone()
            
            self.animation_bar.addTopLevelItem(widget)
            self.animation_bar.setCurrentItem(widget)
         
        
        close_action.triggered.connect(emit_close)
        copy_action.triggered.connect(emit_copy)
        
       
        context_menu.addAction(close_action)
        context_menu.addAction(copy_action)
        context_menu.addAction(self.copy_cells_action)
        context_menu.addAction(self.paste_cells_action)
        
        context_menu.exec(self.mapToGlobal(event.pos()))
        context_menu.destroy()
        del context_menu
    
    def emit_copy_cells(self):
            list = self.table_display.selectedIndexes()
            self.copied_values = []
            #print( list.column() )
            lowest_row = list[0].row()
            lowest_col = list[0].column()
            
            for cell in list:
                item = self.table_display.item(cell.row(), cell.column())
                
                if isinstance(item, QTableWidgetItem):
                    self.copied_values.append( [item.text(), cell.row(), cell.column() ] )
                   
                else:
                    self.copied_values.append( ["", cell.row(), cell.column() ] )
                
                
                lowest_row = min(lowest_row, cell.row())
                lowest_col = min(lowest_col, cell.column())
            print( len( self.copied_values) )
            
            for cell in self.copied_values:
                cell[1] -= lowest_row
                cell[2] -= lowest_col
                     
    def emit_paste_cells(self):
        list = self.table_display.selectedIndexes()
    
        row = list[0].row()
        col = list[0].column()
        
        for cell in self.copied_values:
            eff_row = cell[1] + row
            eff_col = cell[2] + col

            
            self.table_display.setItem(eff_row, eff_col, QTableWidgetItem( cell[0] ))

    def emit_clear_cells(self):
        list = self.table_display.selectedIndexes()
        
        for cell in list:
            item = self.table_display.item(cell.row(), cell.column())
            
            if isinstance(item, QTableWidgetItem):
                item.setText("")
            else:
                self.table_display.setItem(cell.row(), cell.column(), QTableWidgetItem( "" ))

    
    #table info stuff
    
    def load_animation_to_middle(self, index, array = None):      
        
        if array is not None:
            information = array
        else:
            if index < len( list_of_animations ) :
                information = list_of_animations[index].display_info;
            else:
                return
                
        self.table_display.clearContents()
        
        col_count = 1
        first_vals = []
        for i in range(len (information)):
            col_count = max(col_count, len( information [i] ) )
            
            for j in range( len(information[i] )):
                if information[i][j] != "":
                     first_vals.append(information[i][j])
                     break

        self.table_display.setColumnCount(col_count)
        self.table_display.setRowCount(len(information))
        
        
        for row in range(len(information)):
            for col in range(col_count):
                try:
                    self.table_display.setItem(row, col, QTableWidgetItem( str(information[row][col]) ))
                except:
                    pass
        
        
        self.table_display.setHorizontalHeaderLabels(information[1])
        self.table_display.setVerticalHeaderLabels(first_vals)
        
        if array is None:
            filepath = list_of_animations[index].filepath
            if filepath.endswith(".bck") or filepath.endswith(".bca"):
                self.model.setDisabled(False)
                self.convert.setDisabled(False)
            else:
                self.model.setDisabled(True)
                self.convert.setDisabled(False)
        
        
    def selected_animation_changed(self):

        if self.is_remove:
            return;
        
        print("too bad")
        if len(list_of_animations)  > 0:
 

            list_of_animations[self.current_index].display_info = self.get_on_screen()          
            index = self.animation_bar.currentIndex().row()
            print( "new selected index is " + str(index) )
            print( list_of_animations[index].display_info[0] )
            self.current_index = index
            self.load_animation_to_middle(index)       


    def get_on_screen(self):
    
        collected_info = []
        
        
        for i in range( self.table_display.rowCount() ):
            row_info = []
               
            for j in range (self.table_display.columnCount() ):
                item = self.table_display.item(i, j)
                if isinstance(item, QTableWidgetItem):
                    row_info.append(item.text())
                    
                    

                else:
                    row_info.append("")
    
            collected_info.append(row_info)
        return collected_info
            
            
    def display_info_changes(self): #not used anymroe
        global count
        index = self.animation_bar.currentIndex().row() 
        
        #collected_info = []
        
        first_vals = []
        
        for i in range( self.table_display.rowCount() ):
            row_info = []
               
            for j in range (self.table_display.columnCount() ):
                item = self.table_display.item(i, j)
                if isinstance(item, QTableWidgetItem):
                    row_info.append(item.text())
                    
                    #if j == 0:
                    if item.text() != "" and len(first_vals) <= i:
                        first_vals.append(item.text())
                    

                else:
                    row_info.append("")
                    
                    if j == 0:
                        first_vals.append("")
            current_info.append(row_info)
        #print(collected_info)
        
        #self.table_display.clearContents()

        self.table_display.setHorizontalHeaderLabels(current_info[1])
        self.table_display.setVerticalHeaderLabels(first_vals)
        
        print( "display info of " + str(index) + " was changed") 
        
        #list_of_animations[index].display_info = collected_info
        
        
        
        print("new list for the " + str(count) + " time")
        
        count += 1
        for anim in list_of_animations:
            print("new animation")
            print( anim.display_info ) 
       
        #self.load_animation_to_middle(index)
                
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

    args = parser.parse_args()

    app = QApplication(sys.argv)
    

    pikmin_gui = GenEditor()
    pikmin_gui.show()
    
    err_code = app.exec()

    sys.exit(err_code)
