from PyQt5.QtWidgets import QAction, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
import animations.general_animation as j3d
from widgets.yaz0 import compress
from io import BytesIO

class tree_item(QTreeWidgetItem):
    def __init__(self, parent):
        QTreeWidgetItem.__init__(self, parent,1000)
        self.display_info = []
        self.filepath = ""
        self.compressed = False
        
    def set_values(self, display_info, filepath, compressed ):
        self.display_info = display_info
        self.filepath = filepath
        self.compressed = compressed
        
        forward_i = filepath.rfind("/") + 1
        backwad_i = filepath.rfind("\\") + 1
        
        self.setText(0, filepath[max(forward_i, backwad_i):])
    
    def save_animation(self, other_filepath = ""):
        
        
        if other_filepath != "":
            working_filepath = other_filepath
        else:
            working_filepath = self.filepath
            
        if (working_filepath.endswith("a") and not working_filepath.endswith(".bva")  ):
            info = j3d.fix_array( self.display_info)
            self.convert_to_a(info)
        else: 
            info = j3d.fix_array( self.display_info)
            j3d.sort_filepath(working_filepath, info) 
        
        if self.compressed:
            out = BytesIO()
            with open(working_filepath, "rb") as f:
                out = compress(f)
            with open(working_filepath, "wb") as f:
                f.write(out.getbuffer())
    
    def convert_to_k(self):
        filepath = self.filepath[:-1] + "k"
        info = j3d.fix_array(self.display_info)  
        if self.filepath.endswith(".bca"):                     
            bck = j3d.sort_filepath(filepath, info)
        elif filepath.endswith(".bla"):             
            blk = j3d.sort_filepath(filepath, info)
        
    def convert_to_a(self, info):
    
        info = j3d.fix_array( info )
  
        if self.filepath.endswith(".bck") or self.filepath.endswith(".bca"):

         
            bca = j3d.convert_to_a(self.filepath, info) #this is a pure bck, no saving
            filepath = self.filepath[:-1] + "a"
            with open(filepath, "wb") as f:           
                bca.write_bca(f)
                f.close()
        elif self.filepath.endswith(".blk") or self.filepath.endswith(".bla"):
        
            
            bla = j3d.convert_to_a(self.filepath, info) #this is a pure bck, no saving
            filepath = self.filepath[:-1] + "a"
            with open(filepath, "wb") as f:           
                bla.write_bla(f)
                f.close()
    def add_children(self, strings):
        self.takeChildren()
        for name in strings:
            child = QTreeWidgetItem(self)
            child.setText(0, name)
            child.setDisabled(True)