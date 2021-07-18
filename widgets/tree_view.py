from PyQt5.QtWidgets import QAction, QMenu, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from animation_editor import GenEditor
from widgets.yaz0 import compress
from io import BytesIO
from animations.general_animation import fix_array, sort_filepath
import animations.general_animation as j3d

class animation_bar(QTreeWidget):
    def __init__(self, parent):  
        QTreeWidget.__init__(self, parent = parent)
        self.main_editor = None
        self.setColumnCount(1)
        self.setHeaderLabel("Animations")
        self.setGeometry(0, 50, 200, 850)
        self.resize(800, self.height())
        
        self.curr_item = None
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.run_context_menu)
    def set_main_editor(self, main_window):
        self.main_editor = main_window
    
    
    def run_context_menu(self, pos):
        if self.topLevelItemCount() < 1:
            return
        
        
        
        index = self.currentIndex().row()
        
        #print("context menu triggered")
        
        context_menu = QMenu(self)
        close_action = QAction("Close Current Animation", self)
        #copy_action = QAction("Copy Animation", self)
        
        
        def emit_close():
            
            print(" emit close ")
            
            self.main_editor.is_remove = True
            
            items = self.selectedItems()         
            min_index = 0
            for item in items:
                self.takeTopLevelItem(index)
               
            self.main_editor.table_display.clearContents()  
            
            if self.topLevelItemCount() > 0: 
               
            
            
                print("load the previous animation to the middle. index: " + str(index) )
                self.curr_item = self.currentItem()
                self.main_editor.load_animation_to_middle(self.currentItem())
            else:
                self.main_editor.workaround.setDisabled(True)
                self.bt_add_frames_adv.setDisabled(True)       
                self.save_file_action.setDisabled(True)
                self.save_file_as_action.setDisabled(True)
            self.main_editor.is_remove = False
            print("done with removing")
                            
        def emit_copy():
            items = self.selectedItems()
            
            if ( len(items) > 1):
                return

            current_entry = main_editor.list_of_animations[index]
            copied_entry = all_anim_information.get_copy(current_entry)
            list_of_animations.insert(index + 1, copied_entry)
             
            widget = self.selectedItems()
            widget = widget[0].clone()
            
            self.addTopLevelItem(widget)
            self.setCurrentItem(widget)
         
        
        close_action.triggered.connect(emit_close)
        #copy_action.triggered.connect(emit_copy)
        
       
        context_menu.addAction(close_action)
        
        context_menu.exec(self.mapToGlobal(pos))
        context_menu.destroy()
        del context_menu

