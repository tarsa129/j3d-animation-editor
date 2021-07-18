
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
import widgets.tree_item as tree_item
import widgets.add_frames as frames_widget

class GenEditor(QMainWindow):
    def __init__(self):
    
        super().__init__()
       
        self.copied_values = []
        self.curr_index = 0
        self.prev_index = 0
        self.is_remove = False
        
        self.create_window = None
        self.frames_window = None
         
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
        self.save_file_all_action = QAction("Save All", self)
        self.create_animation = QAction("Create Animation", self)
        #self.combine_animations = QAction("Combine Animations", self)
        self.toggle_dark_theme_action = QAction("Toggle Dark Theme", self) # create an option to toggle dark theme
        
        self.save_file_action.setShortcut("Ctrl+S")
        self.file_load_action.setShortcut("Ctrl+O")
        self.save_file_as_action.setShortcut("Ctrl+Alt+S")
        self.save_file_all_action.setShortcut("Shift+Ctrl+S")
        self.create_animation.setShortcut("Ctrl+N")

        self.file_load_action.triggered.connect(self.button_load_level)
        self.save_file_action.triggered.connect(self.button_save_level)
        self.save_file_as_action.triggered.connect(self.button_save_as)
        self.save_file_all_action.triggered.connect(self.button_save_all)
        self.create_animation.triggered.connect(self.create_new)
        self.toggle_dark_theme_action.triggered.connect(self.toggle_dark_theme)
        
        self.save_file_action.setDisabled(True)
        self.save_file_as_action.setDisabled(True)
        self.save_file_all_action.setDisabled(True)
        
        #self.combine_animations.triggered.connct(self.combine_anims)

        self.file_menu.addAction(self.file_load_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_file_as_action) 
        self.file_menu.addAction(self.save_file_all_action)
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
        
        self.load_bones_all = QAction("Load Bone Names (All Animations)", self)
        self.load_bones_all.triggered.connect(self.load_bone_names_all)
        
        self.match_bones = QAction("Match With .bmd", self)
        self.match_bones.triggered.connect(self.match_bmd)
        self.match_bones.setShortcut("Ctrl+M")
       
        
        self.model.addAction(self.load_bones)
        self.model.addAction(self.load_bones_all)
        self.model.addAction(self.match_bones)
       
        self.model.setDisabled(True)
        
        self.menubar.addAction(self.model.menuAction())
        
        #table operations
        self.table_ops = QMenu(self)
        self.table_ops.setTitle("Row Operations")
        
        self.remove_row_end = QAction("Remove Row from End", self)
        self.remove_row_end.triggered.connect(self.rem_row)
        
        self.remove_row_here = QAction("Remove Current Row", self)
        self.remove_row_here.triggered.connect(self.rem_row_here)
        
        self.add_row_end = QAction("Add Row to End", self)
        self.add_row_end.triggered.connect(self.add_row)
        
        self.add_row_next = QAction("Add Row Here", self)
        self.add_row_next.triggered.connect(self.add_row_here)
        
        self.table_ops.addAction(self.add_row_end)
        self.table_ops.addAction(self.add_row_next)
        self.table_ops.addAction(self.remove_row_end)
        self.table_ops.addAction(self.remove_row_here)
        
        
        self.menubar.addAction(self.table_ops.menuAction())
        
        #main splitter
        
        self.horizontalLayout = QSplitter()
        self.centralwidget = self.horizontalLayout
        self.setCentralWidget(self.horizontalLayout)
        
        #left sidebar
        self.workaroundl = QWidget(self)
        self.left_vbox = QVBoxLayout(self.workaroundl)
        
        #tree view
        
        self.anim_bar = tree_view.animation_bar(self.workaroundl)      
        self.anim_bar.set_main_editor(self)
        self.anim_bar.itemSelectionChanged.connect(self.selected_animation_changed) 
   
        self.left_vbox.addWidget(self.anim_bar)
        
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
        
       #necessary row operations: add material / bone, remove material / bone, remove empty
        
        """
        self.bt_add_row = QPushButton(self)
        self.bt_add_row.setText("Add Row To End")
        self.bt_add_row.clicked.connect(self.add_row)
        
        self.bt_addr_here = QPushButton(self)
        self.bt_addr_here.setText("Add Row Next")
        self.bt_addr_here.clicked.connect(self.add_row_here)  
        """  
        self.bt_rm_row = QPushButton(self)
        self.bt_rm_row.setText("Remove Empty Rows")
        self.bt_rm_row.clicked.connect(self.rem_empty_rows) 

        self.bt_remmat_here = QPushButton(self)
        self.bt_remmat_here.setText("Remove Material / Bone")
        self.bt_remmat_here.clicked.connect(self.rem_material)

        self.bt_add_material = QPushButton(self)
        self.bt_add_material.setText("Add Material / Bone")
        self.bt_add_material.clicked.connect(self.add_material)
        
        self.bt_add_frames_adv = QPushButton(self)
        self.bt_add_frames_adv.setText("Add Frames Dialogue")
        self.bt_add_frames_adv.clicked.connect(self.frames_dialogue)
        
        self.bottom_actions.addWidget(self.bt_addc_here, 0, 0)       
        #self.bottom_actions.addWidget(self.bt_addr_here, 0, 1)
        self.bottom_actions.addWidget(self.bt_add_col, 1 ,0)
        #self.bottom_actions.addWidget(self.bt_add_row, 1, 1)
        self.bottom_actions.addWidget(self.bt_remc_here, 2, 0)
        self.bottom_actions.addWidget(self.bt_remmat_here, 1, 1)
        self.bottom_actions.addWidget(self.bt_rm_col, 3, 0)
        self.bottom_actions.addWidget(self.bt_rm_row, 2, 1)
        self.bottom_actions.addWidget(self.bt_add_material, 0, 1)
        self.bottom_actions.addWidget(self.bt_add_frames_adv, 3, 1)
               
        self.workaround.setDisabled(True)       
        
        self.left_vbox.addWidget(self.workaround)
        
        #self.horizontalLayout.addWidget(self.anim_bar)
        self.horizontalLayout.addWidget(self.workaroundl)
        self.horizontalLayout.addWidget(self.table_display)  

    #file stuff
      
    def button_load_level(self):
        filter =  "All Supported Files(*.bca *.bck *.bla *.blk *.bpk *.brk *.btk *.btp *.bva)"
        filepaths, choosentype = QFileDialog.getOpenFileNames( self, "Open File","" , filter )
            
        for filepath in filepaths:
            if filepath:        

                animation_object = j3d.sort_file(filepath)               
                self.new_animation_from_object(animation_object, filepath)
         
    def universal_save(self, filepath = ""):
        
        current_item = self.anim_bar.currentItem()
        current_item.display_info = self.get_on_screen()
        current_item.save_animation(filepath)
        
    def button_save_level(self):
        self.universal_save()
            
    def button_save_as(self):         
        filter =  "All Supported Files(*.bca *.bck *.bla *.blk *.bpk *.brk *.btk *.btp *.bva)"
        filepath, choosentype = QFileDialog.getSaveFileName(self, "Save File", self.anim_bar.currentItem().filepath, filter)
        if filepath:
            self.universal_save(filepath)
        
    def button_save_all(self):
        for i in range( self.anim_bar.topLevelItemCount() ):
            current_item = self.anim_bar.currentItem()
            current_item.display_info = self.get_on_screen()
            current_item.save_animation()
            item = self.anim_bar.topLevelItem(i);
            item.save_animation();
    
    
    def create_new(self):
        
        if self.create_window is None:
            self.create_window = create_widget.create_window()
            self.create_window.setWindowModality(QtCore.Qt.ApplicationModal)
            self.create_window.exec_()
            
        created_info = self.create_window.get_info() 
        if created_info is not None:
            table = j3d.create_empty( created_info )

            filepath = created_info[0]
            
            self.new_animation_from_array(table, filepath, False)
        
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
            if exten in [".bmd", ".bdl"]:
                anim_exten = self.anim_bar.currentItem().filepath
                anim_exten = anim_exten[anim_exten.rfind("."):].lower()
                if anim_exten in [".bca", ".bck"]:
                    event.acceptProposedAction()
          
    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls:
            url = mime_data.urls()[0]
            filepath = url.toLocalFile()
            exten = filepath[filepath.rfind("."):].lower()
            if exten in [ ".bca", ".bck", ".bla", ".blk", ".bpk", ".brk", ".btk", ".btp", ".bva" ]:
                animation_object = j3d.sort_file(filepath)            
                self.new_animation_from_object(animation_object, filepath)
            elif exten == ".anim": 
                bck = j3d.import_anim_file(filepath)
                filepath = filepath[0:-5] + ".bck"
                self.new_animation_from_object(bck, filepath)
            elif exten == ".fbx":
                bcks = j3d.import_fbx_file(filepath)
                index_of_slash = filepath.rfind("/")
                
                filepath = filepath[0:index_of_slash + 1]
                #print(filepath)
                for bck in bcks:
                    self.new_animation_from_object(bck[1],filepath +  bck[0] + ".bck")
            elif exten in [".bmd", ".bdl"]:
                self.load_bone_names(filepath)
        
    
    #convert stuff
    
    #okay this is just a general ui thing
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
        
        if extension == ".bva":
            self.match_bones.setDisabled(True)
        else:
            self.match_bones.setDisabled(False)
        
        self.model.setDisabled(False)
        if extension in {".bck", ".bca"}:
            self.load_bones.setDisabled(False)
        else:
            self.load_bones.setDisabled(True)
            
        are_no_anims = self.anim_bar.topLevelItemCount() == 0
        self.workaround.setDisabled(are_no_anims)
        self.save_file_action.setDisabled(are_no_anims)
        self.save_file_as_action.setDisabled(are_no_anims)
        self.save_file_all_action.setDisabled(are_no_anims)

     
    def convert_to_k(self):
        current_item = self.anim_bar.currentItem()
        current_item.display_info = self.get_on_screen()
        current_item.convert_to_k()
        
    def convert_to_a(self):
        self.anim_bar.currentItem().convert_to_a()
    
    def import_anim_file(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,
        ".anim files(*.anim)" )
        if filepath:
            bck = j3d.import_anim_file(filepath)
            filepath = filepath[0:-5] + ".bck"
            self.new_animation_from_object(bck, filepath)
      
    def import_fbx_file(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" ,
        ".fbx files(*.fbx)" )
        if filepath:
            bcks = j3d.import_fbx_file(filepath)
            index_of_slash = filepath.rfind("/")
            
            filepath = filepath[0:index_of_slash + 1]
            #print(filepath)
            for bck in bcks:
                self.new_animation_from_object(bck[1],filepath +  bck[0] + ".bck")
                    
    def new_animation_from_object(self, actual_animation_object, filepath):
        #deal with compression and keep track of whether or not to compress it
        compressed = False
        try:
            with open(filepath, "rb") as f:
                header = f.read(4)
                
                if header == b"Yaz0":
                    compressed = True
        except:
            pass
         
        #tree view stuff
        display_info = actual_animation_object.get_loading_information()
      
        
        #self.anim_bar.addTopLevelItem(loaded_animation)
             
        """
        print("loaded animation display info")
        print(loaded_animation.display_info[0])
        print("index of loaded animation in tree view")
        print(self.anim_bar.indexOfTopLevelItem(loaded_animation) )
        """
        print("current list of animations - right after adding new one")
        for i in range(self.anim_bar.topLevelItemCount() ): 
            print(self.anim_bar.itemAt(i, 0).display_info[0])
        
        
        loaded_animation = self.new_animation_from_array(display_info, filepath, compressed)
        
        loaded_animation.add_children( actual_animation_object.get_children_names() )
        
        print("end of new animation from object")
    
    #bmd stuff
    def new_animation_from_array(self, array, filepath, compressed):
        if self.anim_bar.topLevelItemCount() > 0:
            print( "this is not the first loaded animation " ) 
            #print( "the old index is " + str(self.anim_bar.curr_index) )
            #print("load in the current table to index " + str(self.anim_bar.curr_index) )
            #self.anim_bar.itemAt(self.anim_bar.curr_index,0).display_info = self.get_on_screen()
           
           
            self.anim_bar.currentItem().display_info = self.get_on_screen()
            print(self.anim_bar.currentItem().text(0) )
            print( self.anim_bar.currentItem().display_info[0])
        print(self.anim_bar.topLevelItemCount())
        if self.anim_bar.topLevelItemCount() == 0:
            loaded_animation = tree_item.tree_item(self.anim_bar)    
            self.anim_bar.curr_item = loaded_animation
            print("curr_item set " + str( self.anim_bar.curr_item))
        else:
            loaded_animation = tree_item.tree_item(self.anim_bar)    
        loaded_animation.set_values( array, filepath, compressed )
        

        # deal with the various ui stuff
        self.edit_convert_actions(filepath)
        self.setWindowTitle("j3d animation editor - " + filepath)
        self.bt_add_frames_adv.setDisabled(False)       
        self.save_file_action.setDisabled(False)
        self.save_file_as_action.setDisabled(False)
            
        #do the adding
        self.is_remove = True  
        self.anim_bar.curr_item = loaded_animation
        self.anim_bar.setCurrentItem(loaded_animation)
        
        self.load_animation_to_middle(loaded_animation)
          
        
     
        self.is_remove = False
        
        return loaded_animation

    def load_bone_names(self, filename = None):
        filepath = None
        if filename == None or filename == False:
            filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , "Model files (*.bmd *.bdl)")
        print(filepath, filename)
        if filepath or filename:
            
            if filepath:
                strings = self.get_bones_from_bmd(filepath)
            elif filename:
                strings = self.get_bones_from_bmd(filename)
            #index = self.anim_bar.currentIndex().row()
            #information = self.get_on_screen()
            #information = self.list_of_animations[index].display_info
            for i in range( len(strings) ):
                row = 9 * i + 2
                item = self.table_display.item(row, 0)
                if isinstance(item, QTableWidgetItem):
                    item.setText(strings[i])
                else:
                    self.table_display.setItem(i, 0, QTableWidgetItem( strings[i] ) )
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
            
            index = self.anim_bar.currentIndex().row()
            self.edit_anim_bar_children( self.anim_bar.itemAt(0, index), strings)
    
    def load_bone_names_all(self):
        filepath, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , "Model files (*.bmd *.bdl)")
        if filepath:   
            strings = self.get_bones_from_bmd(filepath)
            #index = self.anim_bar.currentIndex().row()
            #information = self.get_on_screen()
            #information = self.list_of_animations[index].display_info
            for j in range( self.anim_bar.topLevelItemCount() ):
                item = self.anim_bar.itemFromIndex(j)
                if item.filepath.endswith(".bca") or item.filepath.endswith(".bck"):
                    info = item.display_info
                    for i in range( len(strings) ):
                        row = 9 * i + 2
                        if row < len( info ) :
                            info[row][0] = strings[i]

            for i in range( len(strings) ):
                row = 9 * i + 2
                item = self.table_display.item(row, 0)
                if isinstance(item, QTableWidgetItem):
                    item.setText(strings[i])
                else:
                    self.table_display.setItem(i, 0, QTableWidgetItem( strings[i] ) )
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
            
            item = self.anim_bar.currentItem()
            item.add_children(strings)
    
    def match_bmd(self):
        index = self.anim_bar.currentIndex().row()
        filepath = self.list_of_animations[index].filepath
        
        bmd_file, choosentype = QFileDialog.getOpenFileName( self, "Open File","" , "Model files (*.bmd *.bdl)" )
        if bmd_file:
            self.list_of_animations[index].display_info = self.get_on_screen()
            info = j3d.fix_array(self.list_of_animations[index].display_info)
            strings = []

            if filepath.endswith(".bck") or filepath.endswith(".bca"):
                strings = self.get_bones_from_bmd(bmd_file)
            elif filepath.endswith(".bva"):
                return
                #string = self.get_meshes_from_bmd(bmd_file)
            else:
                strings = self.get_materials_from_bmd(bmd_file)
            
            array = j3d.match_bmd(filepath, info, strings)                
            self.load_animation_to_middle(index, array )                
            self.edit_anim_bar_children( self.anim_bar.itemAt(0, index), strings)
             
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

    def get_meshes_from_bmd(self, bmd_file):
        strings = []
        with open(bmd_file, "rb") as f:
                s = f.read()
                a = s.find(b'\x53\x48\x50\x31')
                print(a)
                f.seek(a + 0x14);
                address = j3d.read_uint32(f)
                print(address)
                f.seek(address + a)
                strings = j3d.StringTable.from_file(f).strings;
                print(strings)
                f.close()
            
        return strings

    #table view stuff
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
                                
                                index = self.anim_bar.currentIndex().row()   
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
        
        context_menu = QMenu(self.anim_bar)
        
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
            
        #print( len( self.copied_values) )
        
        for cell in self.copied_values:
            cell[1] -= lowest_row
            cell[2] -= lowest_col
                     
    def emit_paste_cells(self):
        list = self.table_display.selectedIndexes()
    
        row = list[0].row()
        col = list[0].column()
        
        max_row_length = self.table_display.columnCount()
        
        for cell in self.copied_values:
            eff_row = cell[1] + row
            eff_col = cell[2] + col
            if eff_col < max_row_length:
            
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
        

    def get_vertical_headers(self, information):
        col_count = max( len(information[0]), len(information[1]))
        first_vals = []
        first_vals.append( information[0][0] )
        first_vals.append( information[1][0] )
        for i in range(2, len(information)):
            col_count = max(col_count, len( information [i] ) )
            
            for j in range( len(information[i] )):          
   
                if not information[i][j] in ["LLLL", "SSSS", "Texture Index", "Center", "Register", "Constant", "Linear", "Smooth"]:
                   
                    if not str(information[i][j]).isnumeric() and information[i][j] != "":
                      
                        if not str(information[i][j]).startswith("("):
                   
                            first_vals.append(str(information[i][j]))
                            break
        return (first_vals, col_count)

    #table info stuff
    
    def fix_table(self, information, col_count):
        for row in range(len(information)):
            for col in range(col_count):
                if len( information[row] ) > col:
                    if information[row][col] == "LLLL" or ( col == 1 and information[row][col] == "Linear"):
                        icon = QIcon("icons/linear.png")
                        item = QTableWidgetItem(icon, "Linear")
                        item.setWhatsThis("The tanget interpolation mode")
                    elif information[row][col] == "SSSS" or ( col == 1 and information[row][col] == "Smooth"):
                        icon = QIcon("icons/smooth.png")
                        item = QTableWidgetItem(icon, "Smooth")
                    else:
                        item = QTableWidgetItem(str(information[row][col]) )
                    self.table_display.setItem(row, col, item)
    
    #ONLY loads what it is given, backup MUST be done before calling this
    def load_animation_to_middle(self, treeitem):      
        
        print("beginning of load animation to middle")
        
        self.table_display.clearContents()
        
        print("new loaded animation")
        print(treeitem)
        
        information = treeitem.display_info
        filepath = treeitem.filepath
        
        first_vals, col_count = self.get_vertical_headers(information)

        self.table_display.setColumnCount(col_count)
        self.table_display.setRowCount(len(information))

        for i in range(self.table_display.rowCount()): # interate through all the rows of the middle table
            self.table_display.setRowHeight(i, 20) # make each row thinner
                
        self.fix_table(information, col_count)
                      
        self.table_display.setHorizontalHeaderLabels(information[1])
        self.table_display.setVerticalHeaderLabels(first_vals)
        
        self.setWindowTitle("j3d animation editor - " + filepath)
        self.edit_convert_actions(filepath)
        


        print("end of load animation to middle")
    def selected_animation_changed(self):

        if self.is_remove:
            return
        
        if self.anim_bar.topLevelItemCount()  > 0:
            #load in previous values
            #print("load in previous value")
            print(self.anim_bar.curr_item.text(0))

            self.anim_bar.curr_item.display_info = self.get_on_screen()          

            self.anim_bar.curr_item = self.anim_bar.currentItem()
            """
            print("updated curr item")
            print(self.anim_bar.curr_item.text(0))
            print( "new selected index is " + str(self.anim_bar.curr_item ) )
            print( self.anim_bar.currentItem().display_info )
            """
            self.load_animation_to_middle(self.anim_bar.currentItem() )
             

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
                             
    def cell_clicked(self, row, column):
        item = self.table_display.item(row, column)
        
        if isinstance(item, QTableWidgetItem):
            icon = item.icon()
            
            if not item.icon().isNull() and column <= 1:
                if item.text().startswith("L"):
                    item.setText("Smooth")
                    icon = QIcon("icons/smooth.png")
                else:
                    item.setText("Linear")
                    icon = QIcon("icons/linear.png")
                item.setIcon(icon)
            elif column == 0:
                if item.text() == "Register":
                    item.setText("Constant")
                elif item.text() == "Constant":
                    item.setText("Register")
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
        if self.anim_bar.topLevelItemCount() > 0:
            minimum = len (self.anim_bar.currentItem().display_info[0] )
            if self.table_display.columnCount() > minimum:
                self.bt_rm_col.setDisabled(False)
        
    def rem_column(self):
        if self.anim_bar.topLevelItemCount() > 0:
            vals = self.anim_bar.currentItem().display_info[0]
            
            minimum = 0;
            
            for i in vals:
                if i != "":
                    minimum += 1
            if self.table_display.columnCount() > minimum:
                self.table_display.setColumnCount(self.table_display.columnCount() - 1)
        else:
            self.table_display.setColumnCount(self.table_display.columnCount() - 1)
    
    def add_col_here(self, col_index = None):
        
        if col_index == None or col_index == False:
            curcol = self.table_display.currentColumn() + 2
        else:
            curcol = col_index
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
            index = self.anim_bar.currentIndex().row()
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
    
    def add_row(self, value = None):
        self.table_display.setRowCount(self.table_display.rowCount() + 1)
        self.table_display.setRowHeight(self.table_display.rowCount() - 1, 20)
        
        self.bt_rm_row.setDisabled(self.table_display.rowCount() <= 2)
        print(value)
        if value is not None and value is not False:
            
            for i in range(len (value)):
                new_item = QTableWidgetItem( str(value[i] ))
                self.table_display.setItem(self.table_display.rowCount() - 1, i, new_item)

    def rem_empty_rows(self):
        print("column count " + str( self.table_display.columnCount() ) )
        if self.anim_bar.topLevelItemCount() > 0:
            for i in reversed(range( 2, self.table_display.rowCount() )):
                is_empty = True
                j = 0
                while is_empty and j < self.table_display.columnCount():
                    item = self.table_display.item(i, j)
                    if item is not None and item.text() != "":
                        is_empty = False
                    j += 1
                if is_empty:
                    print( "removing row " + str(i) )
                    self.rem_row_here(i)
                    i -= 1
                    
                
    
    def rem_row(self):
        if self.table_display.rowCount() > 2:
            self.table_display.setRowCount(self.table_display.rowCount() - 1)
        if self.table_display.rowCount() == 2:
            self.bt_rm_row.setDisabled(True)
    
    def add_row_here(self, currow):
        if currow is not False and currow is not None:
            currow += 1
        else:
            currow = self.table_display.currentRow()
        #currow = self.table_display.currentRow() + 1
        
        self.add_row()
        if currow > 2:
            for i in reversed( range( currow, self.table_display.rowCount() ) ):
                for j in range( 0, self.table_display.columnCount() ):
                    if i != currow:
                        old = self.table_display.item(i - 1, j)
                        
                        
                        if old is not None:
                            self.table_display.setItem(i, j, old.clone())
                    else:
                        self.table_display.setItem(i, j, QTableWidgetItem(""))
                    """
                    except:
                        new = QTableWidgetItem("")
                        self.table_display.setItem(i - 1, j, QTableWidgetItem(""))
                    #self.table_display.setItem(i, j, new)
                    self.table_display.setItem(i, j, old.clone())
                    """
    
    def find_row(self, step, look_col, start, end):
            row = self.table_display.currentRow()
            stop_row =  self.table_display.rowCount()
            found = False
            while found == False and row > 1 and row < stop_row:
                item = self.table_display.item(row, look_col)
                if item is not None and item.text().lower().startswith(start) and item.text().lower().endswith(end):
                    found = True
                else:
                    row += step
            
            if not found:
                return None
            else:
                return row
    
    def rem_material(self):
        if self.anim_bar.topLevelItemCount() > 0:
            extension = self.anim_bar.currentItem().filepath
            extension = extension[-4:]
            if extension in [ ".bla" ,".blk", ".bva", ".btp"]:
                self.rem_row_here()
            else:
                look_col = 2
                top_row  = self.table_display.currentRow()
                bot_row = self.table_display.currentRow()
                if extension in [".bca", ".bck"]:
                    # look for scalex and to transz
                    
                    top_row = self.find_row(-1, look_col, "scale", "x:")
                    if top_row is None:
                        return 
                    bot_row = self.find_row(1, look_col, "trans", "z:" )
                    if bot_row is None:
                        return

                    print(top_row, bot_row)
                
                    
                elif extension == ".btk":
                    top_row = self.find_row(-1, look_col, "scale", "u:")
                    if top_row is None:
                        return 
                    bot_row = self.find_row(1, look_col, "trans", "w:" )
                    if bot_row is None:
                        return

                    print(top_row, bot_row)
                elif extension in [".brk", ".bpk"]:
                    if extension == ".bpk":
                        look_col = 1
                    top_row = self.find_row(-1, look_col, "re", "d:")
                    if top_row is None:
                        return 
                    bot_row = self.find_row(1, look_col, "alp", "ha:" )
                    if bot_row is None:
                        return
                    # look for red and alpha
                for i in range(top_row, bot_row + 1):
                    self.rem_row_here(top_row)
                information = self.get_on_screen()
                first_vals, col_count = self.get_vertical_headers(information)
                self.table_display.setVerticalHeaderLabels(first_vals)
                self.fix_table(information, col_count)
                
    def rem_row_here(self, currow = None):
        if currow is None or currow == False:
            currow = self.table_display.currentRow()
        if currow == 0:
            self.rem_row()
        elif self.anim_bar.topLevelItemCount() > 0:       
            currow += 1
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
        if self.anim_bar.topLevelItemCount() > 0:
            extension = self.anim_bar.currentItem().filepath
            extension = extension[-4:]
            
            rows_to_add = 0
            
            
            
            if extension == ".bla" or extension == ".blk":
                self.add_row(["Cluster #"])
            elif extension == ".btp":
                self.add_row(["Material Name"])
            elif extension == ".bva":
                self.add_row(["Mesh #"])
            else:
                single_mat = j3d.get_single_mat(extension)
                for i in range( len(single_mat)):
                    self.add_row(single_mat[i])
           
            
            for i in range( rows_to_add ):
                self.add_row()
            
            information = self.get_on_screen()
            first_vals, col_count = self.get_vertical_headers(information)
            self.table_display.setVerticalHeaderLabels(first_vals)
            self.fix_table(information, col_count)
            
    
    def frames_dialogue(self):
        if self.frames_window is None:
            self.frames_window = frames_widget.frames_window()
            self.frames_window.setWindowModality(QtCore.Qt.ApplicationModal)
            self.frames_window.exec_()
            
        frames_to_add = self.frames_window.get_info()    

        
        if frames_to_add is not None:
        
            extension = self.anim_bar.currentItem().filepath
            info = self.get_on_screen()
            extension = extension[-4:]
            
            register_index = -1
            constant_index = -1
            
            duration = int( info[0][3] )
            if extension in [".btk", ".bca", ".bck"]:
                duration = int( info[0][5] )
            if len(frames_to_add) >= 3 and frames_to_add[2] == "duration":              
                frames_to_add = [ *range(frames_to_add[1], duration + 1, frames_to_add[0]) ]
           
            frames_column = 2
            if extension in [".bca", ".bck", ".btk", ".brk"]:
                frames_column = 3
            elif extension == ".blk":
                frames_column = 1
            
         
            if frames_to_add[-1] > duration:
                new = QTableWidgetItem(str(frames_to_add[-1]))
                duration = frames_to_add[-1]
                if extension in [".btk", ".bca", ".bck"]:
                    self.table_display.setItem(0, 5, new)
                else:
                    self.table_display.setItem(0, 3, new)
            
            keyframes = []
            
                
            before_adding = [0, frames_column]

            for i in range( frames_column, len(info[frames_row]) ):
                cell_text = info[frames_row][i].strip()
                if cell_text != "":
                    if not cell_text.isnumeric():
                        cell_text = cell_text[6:]
                            
                    cell_text = int(cell_text)
                    if cell_text in frames_to_add:
                        frames_to_add.remove(cell_text)                    
                    if cell_text <= frames_to_add[0] and cell_text > before_adding[0]:
                        before_adding = [cell_text, i]
                        
                    
                    if cell_text > frames_to_add[0]:
                        keyframes.append( (cell_text, i) )
            #assume keyframes are sorted
            """
            print(before_adding)
            print (keyframes)
            print(frames_to_add)
            print("-")
            """
            frames_added = 0
            keyframes_passed = 0
            
            for frame in frames_to_add:

                
                if len(keyframes) == 0:
                    insertion_column = before_adding[1] + keyframes_passed
                    print("len is zero")
                    #before_adding[1] += 1
                elif frame < keyframes[0][0]:
                    insertion_column = keyframes[0][1] -1
                    print("frame " + str(frame) + " is less than first keyframe ", end = "")
                elif frame > keyframes[0][0]:
                    insertion_column = keyframes[0][1]
                    keyframes.pop(0)
                    keyframes_passed += 1
                    print("frame " + str(frame)+ " is greater than first keyframe ", end = "")
                
                insertion_column += frames_added + 2
                print(insertion_column) 
                self.add_col_here(insertion_column)
                frames_added += 1
                
                new = QTableWidgetItem("Frame " + str(frame))
                self.table_display.setItem(frames_row, insertion_column - 1, new)
                
        
        self.table_display.setHorizontalHeaderLabels(self.get_on_screen()[1])
        self.frames_window = None
        
import sys
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

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
