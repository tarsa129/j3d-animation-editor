import struct


BTPFILEMAGIC = b"J3D1btp1"
BTKFILEMAGIC = b"J3D1btk1"
BRKFILEMAGIC = b"J3D1brk1"
BCKFILEMAGIC = b"J3D1bck1"
BPKFILEMAGIC = b"J3D1bpk1"
BCAFILEMAGIC = b"J3D1bca1"

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


class basic_animation(object):
    def __init__(self):
        pass

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
        keys.append(i)
   
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
    for i in range( len( info )):
        while info[i][-1] == "":
            info[i].pop( len( info[i]) - 1 )
    for i in range( len( info )):
        if len( info[i]) == 0:
            info.pop(i)  
    #print(info)
    return info 
    
def make_tangents(array):
    if len( array ) == 1:
        return array
    for i in range( len( array ) - 1):
        this_comp = array[i]
        next_comp = array[i+ 1]
        
        tangent = (next_comp.value - this_comp.value) / (next_comp.time - this_comp.time)
        
        array[i].tangentOut = tangent
        array[i+1].tangentIn = tangent
    
    this_comp = array[-1]
    next_comp = array[0]
    
    tangent = (next_comp.value - this_comp.value) / (next_comp.time - this_comp.time)
        
    array[-1].tangentOut = tangent
    array[0].tangentIn = tangent
    
    #print( array)
    
    return array

def convert_to_k(filepath, info):
    if filepath.endswith(".bck"):
        from animations.bck import bck
        import animations.bck as bck_file
        bca = bck_file.bck.get_bca(info) 
        return bca

def sort_file(filepath):
    with open(filepath, "rb") as f:
        magic = f.read(8)
        print(magic)
        
        if magic == BTPFILEMAGIC:
            from animations.btp import btp
            import animations.btp as btp_file
            return btp_file.btp.from_anim(f)       
        elif magic == BTKFILEMAGIC:
            from animations.btk import btk
            import animations.btk as btk_file
            return btk_file.btk.from_anim(f)       
        elif magic == BRKFILEMAGIC:
            from animations.brk import brk
            import animations.brk as brk_file
            return brk_file.brk.from_anim(f)       
        elif magic == BCKFILEMAGIC:
            from animations.bck import bck
            import animations.bck as bck_file
            return bck_file.bck.from_anim(f)      
        elif magic == BPKFILEMAGIC:
            from animations.bpk import bpk
            import animations.bpk as bpk_file
            return bpk_file.bpk.from_anim(f)          
        elif magic == BCAFILEMAGIC:
            from animations.bca import bca
            import animations.bca as bca_file
            return bca_file.bca.from_anim(f)
        f.close()
            
def sort_filepath(filepath, information):
    print(filepath)
    if filepath.endswith(".btp"):
        from animations.btp import btp
        import animations.btp as btp_file
        return btp_file.btp.from_table(filepath, information)
    elif filepath.endswith(".btk"):
        from animations.btk import btk
        import animations.btk as btk_file
        return btk_file.btk.from_table(filepath, information)  
    elif filepath.endswith(".brk"):
         from animations.brk import brk
         import animations.brk as brk_file
         return brk_file.brk.from_table(filepath, information)  
    elif filepath.endswith(".bck"):
         from animations.bck import bck
         import animations.bck as bck_file
         return bck_file.bck.from_table(filepath, information) 
    elif filepath.endswith(".bpk"):
         from animations.bpk import bpk
         import animations.bpk as bpk_file
         return bpk_file.bpk.from_table(filepath, information) 
    elif filepath.endswith(".bca"):
         from animations.bca import bca
         import animations.bca as bca_file
         return bca_file.bca.from_table(filepath, information) 
         

