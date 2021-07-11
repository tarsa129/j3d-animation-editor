import struct
from animations.fbx_scripts import import_fbx_file
import animations.fbx_scripts as fs
from widgets.yaz0 import decompress
from io import BytesIO

BTPFILEMAGIC = b"J3D1btp1"
BTKFILEMAGIC = b"J3D1btk1"
BRKFILEMAGIC = b"J3D1brk1"
BCKFILEMAGIC = b"J3D1bck1"
BPKFILEMAGIC = b"J3D1bpk1"
BCAFILEMAGIC = b"J3D1bca1"
BLAFILEMAGIC = b"J3D1bla1"
BLKFILEMAGIC = b"J3D1blk1"
BVAFILEMAGIC = b"J3D1bva1"


PADDING = b"This is padding data to align"

def read_uint32(f):
    return struct.unpack(">I", f.read(4))[0]
def read_uint16(f):
    return struct.unpack(">H", f.read(2))[0]
def read_sint16(f):
    return struct.unpack(">h", f.read(2))[0]
def read_uint8(f):
    return struct.unpack(">B", f.read(1))[0]
def read_sint8(f):
    return struct.unpack(">b", f.read(1))[0]
def read_float(f):
    return struct.unpack(">f", f.read(4))[0]
    
    
def write_uint32(f, val):
    f.write(struct.pack(">I", val))
def write_uint16(f, val):
    f.write(struct.pack(">H", val))
def write_sint16(f, val):
    f.write(struct.pack(">h", val))
def write_uint8(f, val):
    f.write(struct.pack(">B", val))
def write_sint8(f, val):
    f.write(struct.pack(">b", val))
def write_float(f, val):
    f.write(struct.pack(">f", val))

def write_padding(f, multiple):
    next_aligned = (f.tell() + (multiple - 1)) & ~(multiple - 1)
    
    diff = next_aligned - f.tell()
    
    for i in range(diff):
        
        pos = i%len(PADDING)
        f.write(PADDING[pos:pos+1])

loop_mode = ("Play once", "Unknown", "Loop", "Mirror once", "Mirror")
tan_type = ("Tan out only", "Tan in and out") 

class basic_animation(object):
    def __init__(self):
        pass
        
    def get_children_names(self):
        strings = []
        
        for animation in self.animations:
            strings.append(animation.name)
        return strings
    
    @classmethod
    def match_bmd(cls, object, strings):
                      
        i = 0
        while i < len( object.animations):
            anim = object.animations[i]
            if not anim.name in strings:
                object.animations.pop(i)
            else:
                i += 1
        
        return object
        

class AnimComponent(object):
    def __init__(self, time, value, tangentIn = 0, tangentOut=None, tantype = "0"):
        self.time = time 
        self.value = value
        self.tangentIn = tangentIn 
        self.tanType = tantype
        
        #self.tan_inter = -1
        
        if tangentOut is None:
            self.tangentOut = tangentIn
        else:
            self.tangentOut = tangentOut
    
    def serialize(self):
        return [self.time, self.value, self.tangentIn, self.tangentOut]
    
    def __repr__(self):
        return "Time: {0}, Val: {1}, TanIn: {2}, TanOut: {3}".format(self.time, self.value, self.tangentIn, self.tangentOut).__repr__()
    
    def convert_rotation(self, rotscale):
        self.value *= rotscale 
        self.tangentIn *= rotscale
        self.tangentOut *= rotscale
        
    def convert_rotation_inverse(self, rotscale):
        self.value /= rotscale 
        self.tangentIn /= rotscale
        self.tangentOut /= rotscale
    
    
    @classmethod
    def from_array(cls, offset, index, count, valarray, tanType):
        if count == 1:
            return cls(0, valarray[offset+index], 0, 0)
            
        
        else:
            if tanType == 0:
                return cls(valarray[offset + index*3], valarray[offset + index*3 + 1], valarray[offset + index*3 + 2])
            elif tanType == 1:
                return cls(valarray[offset + index*4], valarray[offset + index*4 + 1], valarray[offset + index*4 + 2], valarray[offset + index*4 + 3])
            else:
                raise RuntimeError("unknown tangent type: {0}".format(tanType))

def combine_dicts(array, keyframes_dictionary):
    thismat_kf = {}
    
    for value in array:
        thismat_kf[value.time] = value.value
        
    for k in keyframes_dictionary.keys(): #if there is a keyframe that does not apply to the current material, pad
        if not k in thismat_kf.keys():
            keyframes_dictionary[k].append("")
        
    for k in thismat_kf.keys():
        if k in keyframes_dictionary: 
            keyframes_dictionary[k].append(thismat_kf[k])
        else:
            to_add = []
            for l in range(int( len(keyframes_dictionary[0]) - 1  )):
                to_add.append("")
            to_add.append(thismat_kf[k])
            keyframes_dictionary[k] = (to_add)  
    
    return keyframes_dictionary


def write_values(info, keyframes_dictionary, row):
    keys = []

    for i in keyframes_dictionary.keys():
        keys.append( int(i) )
   
    keys.sort()
    
    for i in keys: #i is the frame, so for each keyframe
       
        info[row].append("Frame " + str( (int(i)) ) ) #add the header
        
        k = row + 1 #k in the row index in the table
        for j in keyframes_dictionary[i]: #j is the value
            #print( len (keyframes_dictionary[i] ) ) 
            try:
                info[k].append(j)
                k += 1      
            except:
                pass
    

class StringTable(object):
    def __init__(self):
        self.strings = []
    
    @classmethod
    def from_file(cls, f):
        stringtable = cls()
        
        start = f.tell()
        
        string_count = read_uint16(f)
        f.read(2) # 0xFFFF
        
        offsets = []
        
        print("string count", string_count)
        
        for i in range(string_count):
            hash = read_uint16(f)
            string_offset = read_uint16(f)
            
            offsets.append(string_offset)
        
        for offset in offsets:
            f.seek(start+offset)
            
            # Read 0-terminated string 
            string_start = f.tell()
            string_length = 0
            
            while f.read(1) != b"\x00":
                string_length += 1 
            
            f.seek(start+offset)
            
            if string_length == 0:
                stringtable.strings.append("")
            else:
                stringtable.strings.append(f.read(string_length).decode("shift-jis"))
            
        return stringtable 
    
    @classmethod
    def hash_string(cls, string):
        hash = 0
        
        for char in string:
            hash *= 3 
            hash += ord(char)
            hash = 0xFFFF & hash  # cast to short 
        
        return hash
    
    @classmethod
    def write(cls, f, strings):
        start = f.tell()
        f.write(struct.pack(">HH", len(strings), 0xFFFF))
        
        for string in strings:
            hash = StringTable.hash_string(string)
            
            f.write(struct.pack(">HH", hash, 0xABCD))
        
        offsets = []
        
        for string in strings:
            offsets.append(f.tell())
            f.write(string.encode("shift-jis"))
            f.write(b"\x00")

        end = f.tell()

        for i, offset in enumerate(offsets):
            f.seek(start+4 + (i*4) + 2)
            write_uint16(f, offset-start)

        f.seek(end)
        
# Optional rounding
def opt_round(val, digits):
    if digits is None:
        return val
    else:
        return round(val, digits)

# Find the start of the sequence seq in the list in_list, if the sequence exists
def find_sequence(in_list, seq):
    matchup = 0
    start = -1

    found = False
    started = False

    for i, val in enumerate(in_list):
        if val == seq[matchup]:
            if not started:
                start = i
                started = True

            matchup += 1
            if matchup == len(seq):
                #start = i-matchup
                found = True
                break
        else:
            matchup = 0
            start = -1
            started = False
    if not found:
        start = -1


    return start

def find_single_value(in_list, value):
    
    return find_sequence(in_list, [value])
    
def fix_array(info):
    # the arrays should be pure text
    for i in range( len( info )):
        while len( info[i]) > 0 and info[i][-1] == "":
                info[i].pop( len( info[i]) - 1 )
    i = 0
    while i < len(info) :
        if len( info[i] ) == 0:
            info.pop(i)
        else:
            i += 1
    
    # fix the header stuff
    for i in range( len( info[0]) ):
        if info[0][i] in loop_mode:
            info[0][i] = str( loop_mode.index( info[0][i] ) )
        elif info[0][i] in tan_type:
            info[0][i] = str( tan_type.index( info[0][i] ) )
            
            
    for i in range (2, len (info[1]) ):
        if str(info[1][i]).isnumeric():
            info[1][i] = "Frame " + info[1][i]
        
            
    #print(info)
    return info 
    
def make_tangents(array, inter = 0 ):
    if len( array ) == 1:
        return array
    elif inter == 1 or inter == -1:
        for i in range( len( array ) ):    
            array[i].tangentOut = 0
            array[i].tangentIn = 0
    else:
        for i in range( len( array ) - 1):
            this_comp = array[i]
            next_comp = array[i+ 1]
            
            tangent = 0
            if next_comp.time != this_comp.time:       
                tangent = (next_comp.value - this_comp.value) / (next_comp.time - this_comp.time)
            
            array[i].tangentOut = tangent
            array[i+1].tangentIn = tangent

        this_comp = array[-1]
        next_comp = array[0]
        
        tangent = 0
        if next_comp.time != this_comp.time:       
            tangent = (next_comp.value - this_comp.value) / (next_comp.time - this_comp.time)
        #tangent = (next_comp.value - this_comp.value) / (next_comp.time - this_comp.time)
            
        array[-1].tangentOut = tangent
        array[0].tangentIn = tangent
        
    
    #print( array)
    
    return array

#import statements
import animations.btp as btp_file
import animations.btk as btk_file
import animations.brk as brk_file
import animations.bpk as bpk_file
import animations.bck as bck_file
import animations.bca as bca_file
import animations.blk as blk_file
import animations.bla as bla_file
import animations.bva as bva_file

def convert_to_a(filepath, info):
    if filepath.endswith(".bck") or filepath.endswith(".bca"):
        bck = bck_file.bck.get_bck(info)
        bca = bca_file.bca.from_bck(bck)
        
        return bca
    if filepath.endswith(".blk") or filepath.endswith(".bla"):

        blk = blk_file.blk.get_blk(info)
        bla = bla_file.bla.from_blk(blk)
        
        return bla
        
def import_anim_file(filepath):

    with open(filepath, "r") as f:
        info = bck_file.bck.from_maya_anim(f)
        f.close()
        return info

def import_fbx_file(filepath):
    
    animations = fs.import_fbx_file(filepath)

    return animations
            
    #return bck_file.bck.from_fbx_anim(filepath); 


def sort_file(filepath):
    with open(filepath, "rb") as f:
        magic = f.read(8)
        print(magic)
        
        if magic.startswith(b"Yaz0"):
            decomp = BytesIO()
            decompress(f, decomp)
            #print(decomp)
            f = decomp
            f.seek(0)
        
            magic = f.read(8)
            print(magic)
        
        if magic == BTPFILEMAGIC:
            return btp_file.btp.from_anim(f)       
        elif magic == BTKFILEMAGIC:
            return btk_file.btk.from_anim(f)       
        elif magic == BRKFILEMAGIC:
            return brk_file.brk.from_anim(f)       
        elif magic == BCKFILEMAGIC:
            return bck_file.bck.from_anim(f)      
        elif magic == BPKFILEMAGIC:
            return bpk_file.bpk.from_anim(f)          
        elif magic == BCAFILEMAGIC:
            return bca_file.bca.from_anim(f)
        elif magic == BLAFILEMAGIC:
            return bla_file.bla.from_anim(f) 
        elif magic == BLKFILEMAGIC: 
            return blk_file.blk.from_anim(f) 
        elif magic == BVAFILEMAGIC: 
            return bva_file.bva.from_anim(f) 
        f.close()
            
def sort_filepath(filepath, information):
    print(filepath)
    if filepath.endswith(".btp"):
        return btp_file.btp.from_table(filepath, information)
    elif filepath.endswith(".btk"):
        return btk_file.btk.from_table(filepath, information)  
    elif filepath.endswith(".brk"):
         return brk_file.brk.from_table(filepath, information)  
    elif filepath.endswith(".bck"):
         return bck_file.bck.from_table(filepath, information) 
    elif filepath.endswith(".bpk"):
         return bpk_file.bpk.from_table(filepath, information) 
    elif filepath.endswith(".bca"):
         return bca_file.bca.from_table(filepath, information) 
    elif filepath.endswith(".bla"):
         return bla_file.bla.from_table(filepath, information) 
    elif filepath.endswith(".blk"):
         return blk_file.blk.from_table(filepath, information) 
    elif filepath.endswith(".bva"):
         return bva_file.bva.from_table(filepath, information) 

def create_empty(information):
    table = []
    filepath = information[0]
    if filepath.endswith(".btp"):
        table = btp_file.btp.empty_table(information)
    elif filepath.endswith(".btk"):
        table = btk_file.btk.empty_table(information)  
    elif filepath.endswith(".brk"):
        table = brk_file.brk.empty_table(information)  
    elif filepath.endswith(".bck"):
        table = bck_file.bck.empty_table(information) 
    elif filepath.endswith(".bpk"):
        table = bpk_file.bpk.empty_table(information) 
    elif filepath.endswith(".bca"):
        table = bca_file.bca.empty_table(information) 
    elif filepath.endswith(".bla"):
        table = bla_file.bla.empty_table(information) 
    elif filepath.endswith(".blk"):
        table = blk_file.blk.empty_table(information) 
    elif filepath.endswith(".bva"):
        table = bva_file.bva.empty_table(information) 
    return table

def match_bmd(filepath, information, strings):
    print(filepath)

    if filepath.endswith(".btp"):
        table = btp_file.btp.match_bmd(information, strings) 
    elif filepath.endswith(".btk"):
        table = btk_file.btk.match_bmd(information, strings)   
    elif filepath.endswith(".brk"):
        table = brk_file.brk.match_bmd(information, strings)   
    elif filepath.endswith(".bck") or filepath.endswith(".bca"):
        table = bck_file.bck.match_bmd(information, strings) 
    elif filepath.endswith(".bpk"):
        table = bpk_file.bpk.match_bmd(information, strings) 
    elif filepath.endswith(".blk") or filepath.endswith(".bla"):
        table = blk_file.blk.match_bmd(information, strings) 
    elif filepath.endswith(".bva"):
        table = bva_file.bva.match_bmd(information, strings) 
    return table
    
