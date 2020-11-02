from PyQt5.QtWidgets import QAction, QMenu, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from animation_editor import GenEditor

class animation_bar(QTreeWidget):
    def __init__(self, main_editor, *args, **kwargs):  
        super().__init__(*args)
        self.main_editor = main_editor
        self.setColumnCount(1)
        self.setHeaderLabel("animations")
        self.setGeometry(0, 50, 200, 850)
        self.resize(800, self.height())
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.run_context_menu)
    def run_context_menu(self, pos):
        if len( self.main_editor.list_of_animations ) < 1:
            return
        
        
        
        index = self.currentIndex().row()
        
        #print("context menu triggered")
        
        context_menu = QMenu(self)
        close_action = QAction("Close Current Animation", self)
        #copy_action = QAction("Copy Animation", self)
        
        
        def emit_close():
            
            print(" emit close ")
            
            self.is_remove = True

            
            items = self.selectedItems()         
            if ( len(items) > 1):
                return
            
            item = items[0]
            index = self.indexFromItem(item)
            
            index = index.row()    #index is the thing to be deleted
            print( "the index is " + str(index) )
            
            self.main_editor.list_of_animations.pop(index) #remove from list

            if len( self.main_editor.list_of_animations ) == 0: #if there is nothing left, simply clear and return
                self.main_editor.table_display.clearContents()
                self.takeTopLevelItem(0)
                self.main_editor.is_remove = False
                return
            else: #there are more animations - select the one below item
                self.main_editor.current_index = max(index - 1, 0);
                item = self.itemAt(self.current_index, 0);
                
            print("remove item from the tree")
            self.takeTopLevelItem(index) #triggers selected_animation_changed 
            self.main_editor.table_display.clearContents()  
            
            print("load the previous animation to the middle. index: " + str(index) )
            self.main_editor.load_animation_to_middle(main_editor.current_index)
            
            
            self.setCurrentItem(item)
            self.main_editor.is_remove = False
            
            self.setCurrentItem(item)
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