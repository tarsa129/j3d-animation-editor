import struct


BTPFILEMAGIC = b"J3D1btp1"
BTKFILEMAGIC = b"J3D1btk1"
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


def sort_file(filepath):
    with open(filepath, "rb") as f:
        if f.read(8) == BTPFILEMAGIC:
            from animations.btp import btp
            import animations.btp as btp_file
            return btp_file.btp.from_anim(f)
        f.seek(0)
        if f.read(8) == BTKFILEMAGIC:
            print("what")
            from animations.btk import btk
            import animations.btk as btk_file
            return btk_file.btk.from_anim(f)
            
def sort_filepath(filepath, information):
    if filepath.endswith(".btp"):
        from animations.btp import btp
        import animations.btp as btp_file
        return btp_file.btp.from_table(filepath, information)
        
            
