
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt, QRect, QModelIndex

from PyQt5.QtWidgets import (QWidget, QMainWindow, QFileDialog, QSplitter, 
                             QSpacerItem, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QGridLayout, QMenuBar, QMenu, QAction, QApplication, QStatusBar, QLineEdit,
                             QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem)

from PyQt5.QtGui import QMouseEvent, QImage, QIcon
import PyQt5.QtGui as QtGui

import animations.general_animation as j3d

import widgets.create_anim as create_widget
import widgets.tree_view as tree_view

from fbx import *
import fbx as fbx
import inspect, sys

class GenEditor(QMainWindow):
    def __init__(self):
    
        super().__init__()
       
        self.list_of_animations = []
        self.copied_values = []
        self.current_index = 0;
        self.is_remove = False
        
        self.create_window = None
         
        self.setAcceptDrops(True)
        self.setup_ui()
        

    def setup_ui(self):
        self.resize(2500, 1000)
        self.resize_mw=QAction()
        
        
        self.setWindowTitle("j3d animation editor")
        self.setup_ui_menubar()
        
        # establish UI themes
        self.default_style_sheet = ""
        self.dark_style_sheet = "color: rgb(230, 230, 230); background-color: rgb(40, 40, 40);"  # dark theme, todo: darken disabled text   
        
        self.show()
    
    def toggle_dark_theme(self): # simple little function to swap stylesheets
        if self.styleSheet() == self.default_style_sheet:
            self.setStyleSheet(self.dark_style_sheet)
        else:
            self.setStyleSheet(self.default_style_sheet)
    
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
        #self.combine_animations = QAction("Combine Animations", self)
        self.toggle_dark_theme_action = QAction("Toggle Dark Theme", self) # create an option to toggle dark theme
        
        self.save_file_action.setShortcut("Ctrl+S")
        self.file_load_action.setShortcut("Ctrl+O")
        self.save_file_as_action.setShortcut("Ctrl+Alt+S")
        self.create_animation.setShortcut("Ctrl+N")

        self.file_load_action.triggered.connect(self.button_load_level)
        self.save_file_action.triggered.connect(self.button_save_level)
        self.save_file_as_action.triggered.connect(self.button_save_as)
        self.create_animation.triggered.connect(self.create_new)
        self.toggle_dark_theme_action.triggered.connect(self.toggle_dark_theme)
        
        self.save_file_action.setDisabled(True)
        self.save_file_as_action.setDisabled(True)
        #self.combine_animations.triggered.connct(self.combine_anims)

        self.file_menu.addAction(self.file_load_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action)   
        self.file_menu.addAction(self.create_animation)
        #self.file_menu.addAction(self.combine_animations)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.toggle_dark_theme_action) # add the button to the File menu
        
        self.menubar.addAction(self.file_menu.menuAction())
        self.setMenuBar(self.menubar)
        
        
        #edit menu
        
        self.edit_menu = QMenu(self)
        self.edit_menu.setTitle("Edit")

        self.copy_cells_action = QAction("Copy Selected Cells", self)
        self.paste_cells_action = QAction("Paste Selected Cells", self)  
        self.clear_cells_action = QAction("Clear Selected Cells", self)
        self.select_all_action = QAction("Select All Cells", self)
        
        self.copy_cells_action.triggered.connect(self.emit_copy_cells)
        self.paste_cells_action.triggered.connect(self.emit_paste_cells)
        self.clear_cells_action.triggered.connect(self.emit_clear_cells)
        self.select_all_action.triggered.connect(self.emit_select_all)
        
        self.copy_cells_action.setShortcut("Ctrl+C")
        self.paste_cells_action.setShortcut("Ctrl+V")
        self.clear_cells_action.setShortcut("Delete")
        self.select_all_action.setShortcut("Ctrl+A")
        
        self.edit_menu.addAction(self.copy_cells_action)
        self.edit_menu.addAction(self.paste_cells_action)
        self.edit_menu.addAction(self.clear_cells_action)
        self.edit_menu.addAction(self.select_all_action)
        
        self.menubar.addAction(self.edit_menu.menuAction())
        
        #convert menu
        self.convert = QMenu(self)
        self.convert.setTitle("Convert")
        
        self.convert_to_key = QAction("Save as .bck / .blk", self)
        self.convert_to_all = QAction("Save as .bca / .bla", self)
        self.import_anim = QAction("Import Maya .anim", self)
        self.import_fbx = QAction("Import .fbx", self)
        
        self.convert_to_key.triggered.connect(self.convert_to_k)
        self.convert_to_all.triggered.connect(self.convert_to_a)
        self.import_anim.triggered.connect(self.import_anim_file)
        self.import_fbx.triggered.connect(self.import_fbx_file)
        
        self.convert_to_key.setShortcut("Ctrl+K")
        
        self.convert.addAction(self.convert_to_key)
        self.convert.addAction(self.convert_to_all)
        self.convert.addAction(self.import_anim)
        self.convert.addAction(self.import_fbx)
        
        self.convert_to_key.setDisabled(True)
        self.convert_to_all.setDisabled(True)
        
        
        self.menubar.addAction(self.convert.menuAction())
        
        
        #load bmd
        
        self.model = QMenu(self)
        self.model.setTitle("Load .bmd")
        
        self.load_bones = QAction("Load Bone Names", self)
        self.load_bones.triggered.connect(self.load_bone_names)
        self.load_bones.setShortcut("Ctrl+L")
        
        self.match_bones = QAction("Match With .bmd", self)
        self.match_bones.triggered.connect(self.match_bmd)
        self.match_bones.setShortcut("Ctrl+M")
       
        
        self.model.addAction(self.load_bones)
        self.model.addAction(self.match_bones)
       
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
        
        self.animation_bar = tree_view.animation_bar(self, self.workaroundl)       
        self.animation_bar.itemSelectionChanged.connect(self.selected_animation_changed) 
        

        
        self.left_vbox.addWidget(self.animation_bar)
        
        #middle table
        
        
        self.table_display = QTableWidget(self)
        self.table_display.resize(1600, self.height())
        self.table_display.setColumnCount(4)
        self.table_display.setRowCount(4)
        for i in range(self.table_display.rowCount()): # iterate through our initial rows
            self.table_display.setRowHeight(i, 20) # make them thinner       
        self.table_display.setGeometry(400, 50, self.width(), self.height())
        self.table_display.cellClicked.connect(self.cell_clicked)
        
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

        self.bt_add_material = QPushButton(self)
        self.bt_add_material.setText("Add Material / Bone")
        self.bt_add_material.clicked.connect(self.add_material)
        
        self.bottom_actions.addWidget(self.bt_addc_here, 0, 0)       
        self.bottom_actions.addWidget(self.bt_addr_here, 0, 1)
        self.bottom_actions.addWidget(self.bt_add_col, 1 ,0)
        self.bottom_actions.addWidget(self.bt_add_row, 1, 1)
        self.bottom_actions.addWidget(self.bt_remc_here, 2, 0)
        self.bottom_actions.addWidget(self.bt_remr_here, 2, 1)
        self.bottom_actions.addWidget(self.bt_rm_col, 3, 0)
        self.bottom_actions.addWidget(self.bt_rm_row, 3, 1)
        self.bottom_actions.addWidget(self.bt_add_material, 4, 0)
               
        self.left_vbox.addWidget(self.workaround)
        
        #self.horizontalLayout.addWidget(self.animation_bar)
        self.horizontalLayout.addWidget(self.workaroundl)
        self.horizontalLayout.addWidget(self.table_display)  


    #file stuff
      
    def button_load_level(self):
        filter =  "All Supported Files(*.bca *.bck *.bla *.blk *.bpk *.brk *.btk *.btp *.bva)"
        filepaths, choosentype = QFileDialog.getOpenFileNames( self, "Open File","" , filter )
            
        for filepath in filepaths:
            if filepath:        

                animation_object = j3d.sort_file(filepath)
                
                self.universal_new_animation(animation_object, filepath)
            

    def button_save_level(self):
        index = self.animation_bar.currentIndex().row()      
        self.list_of_animations[index].display_info = self.get_on_screen()
        info = j3d.fix_array(self.list_of_animations[index].display_info)
        if (self.list_of_animations[index].filepath.endswith("a") and not self.list_of_animations[index].filepath.endswith(".bva")  ):
            self.convert_to_a()
        else: 
            j3d.sort_filepath(self.list_of_animations[index].filepath, info) 
    
    def button_save_as(self): 
        index = self.animation_bar.currentIndex().row()
        
        filter =  "All Supported Files(*.bca *.bck *.bla *.blk *.bpk *.brk *.btk *.btp *.bva)"
        filepath, choosentype = QFileDialog.getSaveFileName(self, "Save File", self.list_of_animations[index].filepath, filter)
        if filepath:
            
            self.list_of_animations[index].display_info = self.get_on_screen()
            info = j3d.fix_array(self.list_of_animations[index].display_info)
            if (self.list_of_animations[index].filepath.endswith(".bca") ):
                self.convert_to_a()
            else: 
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
            
            if len( self.list_of_animations ) > 0:
                index = self.animation_bar.currentIndex().row()
                self.list_of_animations[index].display_info = self.get_on_screen()
            
            self.list_of_animations.append(new_anim)            
            loaded_animation = QTreeWidgetItem(self.animation_bar)
            
            filename = filepath[filepath.rfind("/") + 1:]
            loaded_animation.setText(0, filename)
            
            self.edit_convert_actions(filename)
            
            
            self.is_remove = True 
            self.animation_bar.addTopLevelItem(loaded_animation)       
            self.current_index = len(self.list_of_animations) - 1
            self.load_animation_to_middle(len(self.list_of_animations) - 1)
            self.animation_bar.setCurrentItem(loaded_animation)
            
            self.save_file_action.setDisabled(False)
            self.save_file_as_action.setDisabled(False)
            
            self.is_remove = False
        
        self.create_window = None
               
    def combine_anims(self):
        import widgets.quick_change as quick_change
            
        quick_change_window = quick_change.quick_editor()  
        quick_change_window.setWindowModality(QtCore.Qt.ApplicationModal)            
        quick_change_window.exec_()
    
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls:
            url = mime_data.urls()[0]
            filepath = url.toLocalFile()
            exten = filepath[filepath.rfind("."):].lower()
            if exten in [ ".bca", ".bck", ".bla", ".blk", ".bpk", ".brk", ".btk", ".btp", ".bva", ".anim", ".fbx" ]:
                event.acceptProposedAction()
 
            
    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls:
            url = mime_data.urls()[0]
            filepath = url.toLocalFile()
            exten = filepath[filepath.rfind("."):].lower()
            if exten in [ ".bca", ".bck", ".bla", ".blk", ".bpk", ".brk", ".btk", ".btp", ".bva" ]:
                animation_object = j3d.sort_file(filepath)            
                self.universal_new_animation(animation_object, filepath)
            elif exten == ".anim": 
                bck = j3d.import_anim_file(filepath)
                filepath = filepath[0:-5] + ".bck"
                self.universal_new_animation(bck, filepath)
            elif exten == ".fbx":
                bcks = j3d.import_fbx_file(filepath)
                index_of_slash = filepath.rfind("/")
                
                filepath = filepath[0:index_of_slash + 1]
                print(filepath)
                for bck in bcks:
                    self.universal_new_animation(bck[1],filepath +  bck[0] + ".bck")
        print(event.mimeData().text() )
    
    #convert stuff
    def edit_convert_actions(self, filename):
        extension = filename[-4:]
        if extension in {".bck", ".blk"}:
            self.convert_to_all.setDisabled(False)
            self.convert_to_key.setDisabled(True)
        elif extension in {".bca", ".bla"}:
            self.convert_to_all.setDisabled(True)
            self.convert_to_key.setDisabled(False)
        else:
            self.convert_to_all.setDisabled(True)
            self.convert_to_key.setDisabled(True)
        
        self.model.setDisabled(False)
        if extension in {".bck", ".bca"}:
            self.load_bones.setDisabled(False)
        else:
            self.load_bones.setDisabled(True)
            
    def convert_to_k(self):
        index = self.animation_bar.currentIndex().row()          
        self.list_of_animations[index].display_info = self.get_on_screen()
        
        filepath = self.list_of_animations[index].filepath
        if filepath.endswith(".bca"):
            filepath = filepath[:-1] + "k"
            info = j3d.fix_array(self.list_of_animations[index].display_info)            
            bck = j3d.sort_filepath(filepath, info)
        elif filepath.endswith(".bla"):
            filepath = filepath[:-1] + "k"
            info = j3d.fix_array(self.list_of_animations[index].display_info)             
            blk = j3d.sort_filepath(filepath, info)
        
    def convert_to_a(self):
        index = self.animation_bar.currentIndex().row()
        filepath = self.list_of_animations[index].filepath
        
        info = self.get_on_screen()
        info = j3d.fix_array( info )
        
        self.list_of_animations[index].display_info = info
        
        
        if filepath.endswith(".bck") or filepath.endswith(".bca"):

         
            bca = j3d.convert_to_a(filepath, info) #this is a pure bck, no saving
            filepath = filepath[:-1] + "a"
            print("new filepath is " + filepath)
            with open(filepath, "wb") as f:           
                bca.write_bca(f)
                f.close()
        elif filepath.endswith(".blk") or filepath.endswith(".bla"):
        
            
            bla = j3d.convert_to_a(filepath, info) #this is a pure bck, no saving
            filepath = filepath[:-1] + "a"
            print("new filepath is " + filepath)
            with open(filepath, "wb") as f:           
                bla.write_bla(f)
                f.close()

            
    
    def import_anim_file(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,
        ".anim files(*.anim)" )
        if filepath:
            bck = j3d.import_anim_file(filepath)
            filepath = filepath[0:-5] + ".bck"
            self.universal_new_animation(bck, filepath)
      
    def import_fbx_file(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,
        ".fbx files(*.fbx)" )
        if filepath:
            bcks = j3d.import_fbx_file(filepath)
            index_of_slash = filepath.rfind("/")
            
            filepath = filepath[0:index_of_slash + 1]
            print(filepath)
            for bck in bcks:
                self.universal_new_animation(bck[1],filepath +  bck[0] + ".bck")
                
            #filepath = filepath[0:-5] + ".bck"
            #self.universal_new_animation(bck, filepath)
      
    def universal_new_animation(self, actual_animation_object, filepath):
        
        new_anim = all_anim_information(filepath)           
        new_anim.display_info = actual_animation_object.get_loading_information()
        
        if len( self.list_of_animations ) > 0:
            print( "this is not the first loaded animation " ) 
            index = self.animation_bar.currentIndex().row()
            print( "the old index is " + str(index) )
            print( self.list_of_animations[index].display_info[0] ) 
            self.list_of_animations[index].display_info = self.get_on_screen()
            print( self.list_of_animations[index].display_info[0] ) 
        
        
        self.list_of_animations.append(new_anim)            
        loaded_animation = QTreeWidgetItem(self.animation_bar)
        
        filename = filepath[filepath.rfind("/") + 1:]
        
        loaded_animation.setText(0, filename)
        
        self.edit_anim_bar_children(loaded_animation, actual_animation_object.get_children_names() )
          
        self.edit_convert_actions(filename)
            
        self.is_remove = True     
        self.animation_bar.addTopLevelItem(loaded_animation)       
        self.current_index = len(self.list_of_animations) - 1
        self.load_animation_to_middle(len(self.list_of_animations) - 1)
        
        self.setWindowTitle("j3d animation editor - " + filepath)
        
        self.animation_bar.setCurrentItem(loaded_animation)
        
        self.save_file_action.setDisabled(False)
        self.save_file_as_action.setDisabled(False)
        
       
        
        self.is_remove = False
    
    def edit_anim_bar_children(self, item, strings):
         item.takeChildren()
         for name in strings:
            child = QTreeWidgetItem(item)
            child.setText(0, name)
            child.setDisabled(True)
               
    #bmd stuff
    def load_bone_names(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , "Model files (*.bmd *.bdl)")
        if filepath:   
            strings = self.get_bones_from_bmd(filepath)
            #index = self.animation_bar.currentIndex().row()
            #information = self.get_on_screen()
            #information = self.list_of_animations[index].display_info
            for i in range( len(strings) ):
                row = 9 * i + 2
                item = self.table_display.item(row, 0)
                if isinstance(item, QTableWidgetItem):
                    item.setText(strings[i])
                else:
                    self.table_display.setItem( QTableWidgetItem( strings[i] ) )
            #self.list_of_animations[index].display_info = information
            #self.load_animation_to_middle(0, information)
            information = self.get_on_screen()
            first_vals = []
            for i in range(len (information)):             
                for j in range( len(information[i] )):                    
                    if information[i][j] == "Linear" or information[i][j] == "Smooth":
                        first_vals.append(information[i][j+1])
                        break
                    if information[i][j] != "":
                        first_vals.append(information[i][j])
                        break
            self.table_display.setVerticalHeaderLabels(first_vals)
            
            index = self.animation_bar.currentIndex().row()
            self.edit_anim_bar_children( self.animation_bar.itemAt(0, index), strings)
    
    def match_bmd(self):
        index = self.animation_bar.currentIndex().row()
        filepath = self.list_of_animations[index].filepath
        
        bmd_file, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , "Model files (*.bmd *.bdl)" )
        if bmd_file:
            self.list_of_animations[index].display_info = self.get_on_screen()
            info = j3d.fix_array(self.list_of_animations[index].display_info)
            strings = []

            if filepath.endswith(".bck") or filepath.endswith(".bca"):
                strings = self.get_bones_from_bmd(bmd_file)
            else:
                strings = self.get_materials_from_bmd(bmd_file)
            
            array = j3d.match_bmd(filepath, info, strings)                
            self.load_animation_to_middle(index, array )                
            self.edit_anim_bar_children( self.animation_bar.itemAt(0, index), strings)
     
        
    def get_bones_from_bmd(self, bmd_file):
        strings = []
        with open(bmd_file, "rb") as f:
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
            
        return strings

    def get_materials_from_bmd(self, bmd_file):
        strings = []
        with open(bmd_file, "rb") as f:
                s = f.read()
                a = s.find(b'\x4D\x41\x54\x33')
                print(a)
                f.seek(a + 0x14);
                address = j3d.read_uint32(f)
                print(address)
                f.seek(address + a)
                strings = j3d.StringTable.from_file(f).strings;
                print(strings)
                f.close()
            
        return strings

    #tree view stuff
    def contextMenuEvent(self, event):
        
        if len( self.list_of_animations ) < 1:
            return
            
        quick_change_action = QAction("Quick Edit Menu", self)
        
        def operations( array, operation ) :
            if operation == 0:
                return array[0] + array[1]
            elif operation == 1:
                return array[0] - array[1]
            elif operation == 2:
                return array[0] * array[1]
            elif operation == 3:
                return array[0] / array[1]
            elif operation == 4:
                sum = 0
                for val in array:
                    sum += val
                return sum / len(array)
        
        def emit_quick_change():
            import widgets.quick_change as quick_change
            
            quick_change_window = quick_change.quick_editor()  
            quick_change_window.setWindowModality(QtCore.Qt.ApplicationModal)            
            quick_change_window.exec_()
            
            info = quick_change_window.get_info() 
            if info is not None :
                 
                
                list = self.table_display.selectedIndexes()
                
                avg_array = []
                for cell in list:
                    
                    item = self.table_display.item(cell.row(), cell.column())

                    if isinstance(item, QTableWidgetItem):
                        if info[0] < 4:
                            try:
                                new_value = operations( [ float(item.text()) , float(info[1])], info[0] )
                                
                                index = self.animation_bar.currentIndex().row()   
                                if self.list_of_animations[index].filepath.endswith(".btp"):
                                    new_value = int( new_value )
                                
                                item.setText(str( new_value) )
                                print(new_value)
                            except:
                                print( "error with " +  item.text())
                        else:
                            print("added")
                            try:
                                avg_array.append( float(item.text()) )
                                
                            except:
                                print("not a numeric value - will be ignored" )
                
                print( len( avg_array) )
                if info[0] >= 4:
                    average = operations(avg_array, info[0] )
                    for cell in list: 
                        item = self.table_display.item(cell.row(), cell.column())
                        try:
                            float(item.text())
                            item.setText( str(average) )
                        except:
                            pass
                            
            del quick_change_window
            
        
        quick_change_action.triggered.connect(emit_quick_change)
        
        context_menu = QMenu(self.animation_bar)
        
        context_menu.addAction(self.copy_cells_action)
        context_menu.addAction(self.paste_cells_action)
        context_menu.addAction(self.clear_cells_action)
        context_menu.addAction(quick_change_action)
        
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
                    self.copied_values.append( [item.text(), cell.row(), cell.column(), item.icon() ] )                  
                else:
                    self.copied_values.append( ["", cell.row(), cell.column(), QIcon() ] )
                               
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

            
            self.table_display.setItem(eff_row, eff_col, QTableWidgetItem(cell[3], cell[0] ))

    def emit_clear_cells(self):
        list = self.table_display.selectedIndexes()
        
        for cell in list:
            item = self.table_display.item(cell.row(), cell.column())
            
            if isinstance(item, QTableWidgetItem):
                item.setText("")
                item.setIcon( QIcon() )
            """else:
                self.table_display.setItem(cell.row(), cell.column(), QTableWidgetItem( "" )) """

    def emit_select_all(self):
        
        
        for i in range( self.table_display.rowCount() ):
            for j in range( self.table_display.columnCount() ) :
                item = self.table_display.item(i, j)
                if isinstance(item, QTableWidgetItem):
                    self.table_display.item(i, j).setSelected(True)
        

    #table info stuff
    
    def load_animation_to_middle(self, index, array = None):      
        
        if array is not None:
            information = array
        else:
            if index < len( self.list_of_animations ) :
                information = self.list_of_animations[index].display_info;
            else:
                return
                
        self.table_display.clearContents()
        
        col_count = 1
        first_vals = []
        for i in range(len (information)):
            col_count = max(col_count, len( information [i] ) )
            
            for j in range( len(information[i] )):                    
                if information[i][j] == "LLLL":
                    first_vals.append(information[i][j+1])
                    break
                if information[i][j] != "":
                    first_vals.append(information[i][j])
                    break

        self.table_display.setColumnCount(col_count)
        self.table_display.setRowCount(len(information))
        for i in range(self.table_display.rowCount()): # interate through all the rows of the middle table
            self.table_display.setRowHeight(i, 20) # make each row thinner
                
        for row in range(len(information)):
            for col in range(col_count):
                if len( information[row] ) > col:
                    if information[row][col] == "LLLL" or ( col == 0 and information[row][col] == "Linear"):
                        icon = QIcon("icons/linear.png")
                        item = QTableWidgetItem(icon, "Linear")
                        item.setWhatsThis("The tanget interpolation mode")
                    elif information[row][col] == "SSSS" or ( col == 0 and information[row][col] == "Smooth"):
                        icon = QIcon("icons/smooth.png")
                        item = QTableWidgetItem(icon, "Smooth")
                    else:
                        item = QTableWidgetItem(str(information[row][col]) )
                    self.table_display.setItem(row, col, item)
                      
        self.table_display.setHorizontalHeaderLabels(information[1])
        self.table_display.setVerticalHeaderLabels(first_vals)
        
        if array is None:
            filepath = self.list_of_animations[index].filepath
            self.setWindowTitle("j3d animation editor - " + filepath)
            self.edit_convert_actions(filepath)
        
    def selected_animation_changed(self):

        if self.is_remove:
            return
        
        if len(self.list_of_animations)  > 0:

            self.list_of_animations[self.current_index].display_info = self.get_on_screen()          
            index = self.animation_bar.currentIndex().row()
            print( "new selected index is " + str(index) )
            print( self.list_of_animations[index].display_info[0] )
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
        
        #self.list_of_animations[index].display_info = collected_info
        
        
        
        print("new list for the " + str(count) + " time")
        
        count += 1
        for anim in self.list_of_animations:
            print("new animation")
            print( anim.display_info ) 
       
        #self.load_animation_to_middle(index)
       
    def cell_clicked(self, row, column):
        item = self.table_display.item(row, column)
        
        if isinstance(item, QTableWidgetItem):
            icon = item.icon()
            
            if not item.icon().isNull() and column == 0:
                if item.text().startswith("L"):
                    item.setText("Smooth")
                    icon = QIcon("icons/smooth.png")
                else:
                    item.setText("Linear")
                    icon = QIcon("icons/linear.png")
                item.setIcon(icon)
            elif row == 0 and column > 0:
                setting = self.table_display.item(row, column - 1).text()
                value = self.table_display.item(row, column).text()
                if setting.startswith("Loop"):
                    options = j3d.loop_mode
                elif setting.startswith("Tan"):
                    options = j3d.tan_type
                else:
                    return
                    
                if value == "" or value not in options:
                    position = -1
                else:
                    position = options.index(value)           
                self.table_display.item(row, column).setText(options[( position + 1) % len(options)])

    #table button stuff   
   
    def add_column(self):
        self.table_display.setColumnCount(self.table_display.columnCount() + 1)
        if len(self.list_of_animations) > 0:
            index = self.animation_bar.currentIndex().row()
            minimum = len (self.list_of_animations[index].display_info[0] )
            if self.table_display.columnCount() > minimum:
                self.bt_rm_col.setDisabled(False)
        
    def rem_column(self):
        if len(self.list_of_animations) > 0:
            index = self.animation_bar.currentIndex().row()
            vals = self.list_of_animations[index].display_info[0]
            
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
        if len(self.list_of_animations) > 0:          
            index = self.animation_bar.currentIndex().row()
            vals = self.list_of_animations[index].display_info[0]
            
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
        self.table_display.setRowHeight(self.table_display.rowCount() - 1, 20)
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
        currow = self.table_display.currentRow() + 1
        if currow == 0:
            self.rem_row()
        elif len(self.list_of_animations) > 0:          
            index = self.animation_bar.currentIndex().row()
            minimum = len (self.list_of_animations[index].display_info[0] )
            
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
            
    def add_material(self):
        if len( self.list_of_animations ) > 0:
            index = self.animation_bar.currentIndex().row()
            extension = self.list_of_animations[index].filepath
            extension = extension[-4:]
            
            rows_to_add = 0
            
            if extension in {".bck", ".bca", ".btk"}:
                rows_to_add = 9
            elif extension in {".brk", ".bpk"}:
                rows_to_add = 4
            elif extension in {".btp", ".blk", ".bla"}:
                rows_to_add =1
            
            for i in range( rows_to_add ):
                self.add_row()
    
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
    pikmin_gui.clipboard = app.clipboard() # we can put stuff on the clipboard with this
    pikmin_gui.show()
    
    err_code = app.exec()

    sys.exit(err_code)
