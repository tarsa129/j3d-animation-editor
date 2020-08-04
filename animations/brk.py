import struct 
#from collections import OrderedDict

from animations.general_animation import *
from animations.general_animation import basic_animation
import animations.general_animation as j3d

BRKFILEMAGIC = b"J3D1brk1"
        
class AnimComponent(object):
    def __init__(self, time, value, tangentIn = 0, tangentOut=None):
        self.time = time 
        self.value = value
        self.tangentIn = tangentIn 
        
        if tangentOut is None:
            self.tangentOut = tangentIn
        else:
            self.tangentOut = tangentOut
    
    def serialize(self):
        return [self.time, self.value, self.tangentIn, self.tangentOut]
    
    def __repr__(self):
        return "Time: {0}, Val: {1}, TanIn: {2}, TanOut: {3}".format(self.time, self.value, self.tangentIn, self.tangentOut).__repr__()
        
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


class ColorAnimation(object):
    def __init__(self, index, name, unknown=0):
        self._index = index 
        #self.matindex = matindex 
        self.name = name 
        self.unknown = unknown 
        
        self.component = {"R": [], "G": [], "B": [], "A": []}

        self._component_offsets = {}
        self._tangent_type = {"R": 1, "G": 1, "B": 1, "A": 1}

    def add_component(self, colorcomp, animcomp):
        self.component[colorcomp].append(animcomp)
    
    @classmethod
    def from_brk(cls, f, name, index, rgba_arrays):
        coloranim = cls(name, index)
        
        for i, comp in enumerate(("R", "G", "B", "A")):
            count, offset, tangent_type = struct.unpack(">HHH", f.read(6)) 
            
            for j in range(count):
                animcomp = AnimComponent.from_array(offset, j, count, rgba_arrays[i], tangent_type)
                coloranim.add_component(comp, animcomp)
        
        unknown = read_uint8(f)
        coloranim.unknown = unknown
        assert f.read(3) == b"\xFF\xFF\xFF"
        
        return coloranim
        
    # These functions are used for keeping track of the offset
    # in the json->brk conversion and are otherwise not useful.
    def _set_component_offsets(self, colorcomp, val):
        self._component_offsets[colorcomp] = val
    
    def _set_tangent_type(self, colorcomp, val):
        self._tangent_type[colorcomp] = val


class brk(object):
    def __init__(self, loop_mode, duration):
        self.register_animations = []
        self.constant_animations = []
        self.loop_mode = loop_mode
        #self.anglescale = anglescale
        self.duration = duration
        #self.unknown_address = unknown_address

    @classmethod
    def from_anim(cls, f):

        size = read_uint32(f)
        #print("Size of brk: {} bytes".format(size))
        sectioncount = read_uint32(f)
        assert sectioncount == 1

        svr_data = f.read(16)
        
        trk_start = f.tell()
        
        trk_magic = f.read(4)
        trk_sectionsize = read_uint32(f)

        loop_mode = read_uint8(f)
        padd = f.read(1)
        assert padd == b"\xFF"
        duration = read_uint16(f)
        brk = cls(loop_mode, duration)

        register_color_anim_count = read_uint16(f)
        constant_color_anim_count = read_uint16(f)
        #print(register_color_anim_count, "register color anims and", constant_color_anim_count, "constant collor anims")
        component_counts = {}
        for animtype in ("register", "constant"):
            component_counts[animtype] = {}
            
            for comp in ("R", "G", "B", "A"):
                component_counts[animtype][comp] = read_uint16(f)
                #print(animtype, comp, "count:", component_counts[animtype][comp])
        
        register_color_animation_offset  = read_uint32(f) + trk_start    # 
        constant_color_animation_offset  = read_uint32(f) + trk_start    #
        register_index_offset            = read_uint32(f) + trk_start    # 
        constant_index_offset            = read_uint32(f) + trk_start    # 
        register_stringtable_offset      = read_uint32(f) + trk_start    #
        constant_stringtable_offset      = read_uint32(f) + trk_start    # 

        offsets = {}
        for animtype in ("register", "constant"):
            offsets[animtype] = {}
            for comp in ("R", "G", "B", "A"):
                offsets[animtype][comp] = read_uint32(f) + trk_start 
                #print(animtype, comp, "offset:", offsets[animtype][comp])
    
        #print(hex(register_index_offset))
        # Read indices
        register_indices = []
        f.seek(register_index_offset)
        for i in range(register_color_anim_count):
            index = read_uint16(f)
            if i != index:
                #print("warning: register index mismatch:", i, index)
                assert(False)
            register_indices.append(index)
        
        constant_indices = []
        f.seek(constant_index_offset)
        for i in range(constant_color_anim_count):
            index = read_uint16(f)
            if i != index:
                #print("warning: constant index mismatch:", i, index)
                assert(False)
            constant_indices.append(index)
        
        # Read stringtable 
        f.seek(register_stringtable_offset)
        register_stringtable = StringTable.from_file(f)
        
        f.seek(constant_stringtable_offset)
        constant_stringtable = StringTable.from_file(f)
        
        # read RGBA values 
        values = {}
        for animtype in ("register", "constant"):
            values[animtype] = {}
            
            for comp in ("R", "G", "B", "A"):
                values[animtype][comp] = []
                count = component_counts[animtype][comp]
                f.seek(offsets[animtype][comp])
                #print(animtype, comp, hex(offsets[animtype][comp]), count)
                for i in range(count):
                    values[animtype][comp].append(read_sint16(f))
        
        for i in range(register_color_anim_count):
            f.seek(register_color_animation_offset + 0x1C*i)
            name = register_stringtable.strings[i]
            anim = ColorAnimation.from_brk(f, i, name, (
                values["register"]["R"], values["register"]["G"], values["register"]["B"], values["register"]["A"]
                ))
            
            brk.register_animations.append(anim)
        
        for i in range(constant_color_anim_count):
            f.seek(constant_color_animation_offset + 0x1C*i)
            name = constant_stringtable.strings[i]
            anim = ColorAnimation.from_brk(f, i, name, (
                values["constant"]["R"], values["constant"]["G"], values["constant"]["B"], values["constant"]["A"]
                ))
            
            brk.constant_animations.append(anim)
        
        return brk 

    def get_children_names(self):
        mat_names = []
        for color_anim in self.register_animations:
            mat_names.append(color_anim.name)
        for color_anim in self.constant_animations:
            mat_names.append(color_anim.name)
        return mat_names

    def get_loading_information(self):

        info = []
        info.append( ["Loop Mode:", self.loop_mode, "Duration:", self.duration] )
        info.append( ["Register Animations"])
        
        keyframes_dictionary = {}
        keyframes_dictionary[0] = []
        
      
        if len (self.register_animations) > 0:   
            print("there are register animations")
            info.append( ["Material Name", "Unknown", "Channel"] )
            
            i = len( info ) 
            
            for anim in self.register_animations:
                info.append( [anim.name, anim.unknown] )
                things = ["Red", "Green", "Blue", "Alpha"]
                
                
                for j in range (len ( things ) ):    
                    comp = things[j]
                    if j == 0:
                        info[i].append(comp)
                    else:
                        info.append( ["", "", comp] )
                
                    thismat_kf = {}
                    array = anim.component[comp[0:1]]
                    
                    #print (array)
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
                    
                
                i = len(info)
                
            for i in keyframes_dictionary.keys(): #i is the frame, so for each keyframe
                info[2].append("Frame " + str( (int(i)) ) ) #add the header
                
                k = 3 #k in the row index in the table
                for j in keyframes_dictionary[i]: #j is the value
                    #print( len (keyframes_dictionary[i] ) ) 
                    try:
                        info[k].append(j)
                        k += 1      
                    except:
                        pass
                        #print("last k: " + str(k))
            
        else:
            print("there are no register animations")
            info[1].append("None")
        
        
        info.append( ["Constant Animations"] )
        
        if len (self.constant_animations) > 0:      
            
            info.append( ["Material Name", "Unknown", "Channel"] )
            
            keyframes_dictionary = {}
            keyframes_dictionary[0] = []   
            
            l = len( info )  
            
            print ("length " + str(l) )

            for anim in self.constant_animations:
                info.append( [anim.name, anim.unknown] )
                things = ["Red", "Green", "Blue", "Alpha"]
                
                
                for j in range (len ( things ) ):    
                    comp = things[j]
                    if j == 0:
                        info[ len (info) - 1 ].append(comp)
                    else:
                        info.append( ["", "", comp] )
                
                    thismat_kf = {}
                    array = anim.component[comp[0:1]]
                    #print (array)
                    for value in array:
                        thismat_kf[int(value.time)] = value.value
                        
                    for k in keyframes_dictionary.keys(): #if there is a keyframe that does not apply to the current material, pad
                        if not k in thismat_kf.keys():
                            keyframes_dictionary[int(k)].append("")
                        
                    for k in thismat_kf.keys():
                        if k in keyframes_dictionary: 
                            keyframes_dictionary[int(k)].append(thismat_kf[k])
                        else: #if it's a new keyframe
                            to_add = []
                            #for count in range(int( len(info) - l - 4 )):
                            for count in range( len(keyframes_dictionary[0]) - 1 ):
                                to_add.append("")
                            to_add.append(thismat_kf[k])
                            keyframes_dictionary[int(k)] = (to_add) 
                    
            print( keyframes_dictionary)
            
            keys = []

            for i in keyframes_dictionary.keys():
                keys.append(i)
         
            keys.sort()
           
            
            for i in keys: #i is the frame, so for each keyframe
                info[l - 1].append("Frame " + str( (int(i)) ) ) #add the header
                #print(keyframes_dictionary[i] ) 
                
                k = l  #k in the row index in the table
                for j in keyframes_dictionary[i]: #j is the value
                    #print( len (keyframes_dictionary[i] ) ) 
                    try:
                        info[k].append(j)
                        k += 1      
                    except:
                        pass
                        #print("last k: " + str(k))
        else:
            info[-1].append("None")
        
        #print(info)
        return info  
    
    @classmethod
    def from_table(cls, f, info):
        brk = cls(int(info[0][1]), int(info[0][3]))
        
        constant_line = 0;
        
        for i in range( len(info) ):
            if info[i][0].startswith("C"):
                constant_line = i
            if constant_line != 0:
                break    
        
        print("constant line " + str(constant_line))
        
        if constant_line > 2: #there are register animations       
            print("there are register animations")
            keyframes = []
            for i in range(3, len( info[2] ) ):
                if info[2][i] != "":
                    text = info[2][i][6:]
                    text = int(text)
                    keyframes.append(text)
            
            #print(keyframes)
            
            for i in range(0, int( constant_line / 4) ):
                curr_line = 4 * i + 3
                
                color_anim = ColorAnimation(i, info[curr_line][0], int( info[curr_line][1] ) )
                
                
                for j in range(0, 4):
                    rgba = "RGBA"
                    rgba = rgba[j: j+1]
                    for k in range(3, len( info[curr_line + j] ) ):
                        if info[curr_line + j][k] != "":
                            anim_comp = AnimComponent(keyframes[k - 3], int(info[curr_line + j][k]) )
                            color_anim.add_component(rgba, anim_comp)
                brk.register_animations.append(color_anim)
                    
        if constant_line + 1 < len( info ):
            print("there are constant animations")
            keyframes = []
            for i in range(3, len( info[constant_line + 1] ) ):
                if info[constant_line + 1][i] != "":
                    text = info[constant_line + 1][i][6:]
                    text = int(text)
                    keyframes.append(text)
            
            for i in range(0, int( (len(info) - constant_line) / 4) ):
                curr_line = constant_line + 4 * i + 2
                            
                color_anim = ColorAnimation(i, info[curr_line][0], int( info[curr_line][1] ) )
                
                
                for j in range(0, 4):
                    rgba = "RGBA"
                    rgba = rgba[j: j+1]
                    for k in range(3, len( info[curr_line + j] ) ):
                        if info[curr_line + j][k] != "":
                            anim_comp = AnimComponent( keyframes[k - 3], int(info[curr_line + j][k]))
                            color_anim.add_component(rgba, anim_comp)
                brk.constant_animations.append(color_anim)
              
        with open(f, "wb") as f:
            brk.write_brk(f)
            f.close()

    
    def write_brk(self, f):
        f.write(BRKFILEMAGIC)
        filesize_offset = f.tell()
        f.write(b"ABCD") # Placeholder for file size
        write_uint32(f, 1) # Always a section count of 1
        f.write(b"SVR1" + b"\xFF"*12)

        trk1_start = f.tell()
        f.write(b"TRK1")

        trk1_size_offset = f.tell()
        f.write(b"EFGH")  # Placeholder for trk1 size
        write_uint8(f, self.loop_mode)
        write_uint8(f, 0xFF)
        
        write_uint16(f, self.duration)
        write_uint16(f, len(self.register_animations))
        write_uint16(f, len(self.constant_animations))
        
        count_offset = f.tell()
        f.write(b"AB"*8)  # Placeholder for register and constant rgba counts
        data_offsets = f.tell()
        f.write(b"ABCD"*6) # Placeholder for data offsets 
        f.write(b"ABCD"*8) # Placeholder for rgba data offsets
        
        write_padding(f, multiple=32)
        assert f.tell() == 0x80
        
        
        register_anim_start = f.tell()
        f.write(b"\x00"*(0x1C*len(self.register_animations)))
        write_padding(f, multiple=4)
        
        constant_anim_start = f.tell()
        f.write(b"\x00"*(0x1C*len(self.constant_animations)))
        write_padding(f, multiple=4)
        


        
        all_values = {}
        
        for animtype, animations in (
        ("register", self.register_animations), 
        ("constant", self.constant_animations)):
        
            all_values[animtype] = {}
            for colorcomp in ("R", "G", "B", "A"):
                all_values[animtype][colorcomp] = []
                
                for anim in animations: 
                    
                
                    animation_components = anim.component[colorcomp]
                    """
                    use_tantype_1 = False 
                    for comp in animation_components:
                        if comp.tangentIn != comp.tangentOut:
                            use_tantype_1 = True 
                            break 
                    
                    if not use_tantype_1:
                        anim._set_tangent_type(colorcomp, 0)"""
                        
                    # Set up offset for scale
                    if len(animation_components) == 1:
                        sequence = [animation_components[0].value]
                    else:
                        sequence = []
                        for comp in animation_components:
                            sequence.append(comp.time)
                            sequence.append(comp.value)
                            sequence.append(comp.tangentIn)
                            sequence.append(comp.tangentOut)
                    
                    offset = j3d.find_sequence(all_values[animtype][colorcomp],sequence)

                    if offset == -1:
                        offset = len(all_values[animtype][colorcomp])
                        all_values[animtype][colorcomp].extend(sequence)
                        
                    anim._set_component_offsets(colorcomp, offset)

        data_starts = []
        for animtype in ("register", "constant"):
            
            for comp in ("R", "G", "B", "A"):
                data_starts.append(f.tell())
                for val in all_values[animtype][comp]:
                    write_sint16(f, val)
                write_padding(f, 4)
                
                
        # Write the indices for each animation
        register_index_start = f.tell()
        for i in range(len(self.register_animations)):
            write_uint16(f, i)
        write_padding(f, multiple=4)
        
        constant_index_start = f.tell()
        for i in range(len(self.constant_animations)):
            write_uint16(f, i)
        write_padding(f, multiple=4)
        
        
        # Create string table of material names for register color animations
        register_stringtable = j3d.StringTable()

        for anim in self.register_animations:
            register_stringtable.strings.append(anim.name)
        
        # Create string table of material names for constant color animations
        constant_stringtable = j3d.StringTable()

        for anim in self.constant_animations:
            constant_stringtable.strings.append(anim.name)
        
        register_stringtable_start = f.tell()
        register_stringtable.write(f, register_stringtable.strings)
        write_padding(f, multiple=4)
        
        constant_stringtable_start = f.tell()
        constant_stringtable.write(f, constant_stringtable.strings)
        write_padding(f, multiple=4)
        
        write_padding(f, multiple=32)
        total_size = f.tell()

        f.seek(register_anim_start)
        for anim in self.register_animations:
            for comp in ("R", "G", "B", "A"):
                write_uint16(f, len(anim.component[comp])) # Scale count for this animation
                write_uint16(f, anim._component_offsets[comp]) # Offset into scales
                write_uint16(f, anim._tangent_type[comp]) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut

            write_uint8(f, anim.unknown)
            f.write(b"\xFF\xFF\xFF")
        
        f.seek(constant_anim_start)
        for anim in self.constant_animations:
            for comp in ("R", "G", "B", "A"):
                write_uint16(f, len(anim.component[comp])) # Scale count for this animation
                write_uint16(f, anim._component_offsets[comp]) # Offset into scales
                write_uint16(f, anim._tangent_type[comp]) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut

            write_uint8(f, anim.unknown)
            f.write(b"\xFF\xFF\xFF")
        
        
        # Fill in all the placeholder values
        f.seek(filesize_offset)
        write_uint32(f, total_size)

        f.seek(trk1_size_offset)
        write_uint32(f, total_size - trk1_start)

        f.seek(count_offset)
        for animtype in ("register", "constant"):
            for comp in ("R", "G", "B", "A"):
                write_uint16(f, len(all_values[animtype][comp]))
                
        # Next come the section offsets
        write_uint32(f, register_anim_start        - trk1_start)
        write_uint32(f, constant_anim_start        - trk1_start)
        write_uint32(f, register_index_start       - trk1_start)
        write_uint32(f, constant_index_start       - trk1_start)
        write_uint32(f, register_stringtable_start - trk1_start)
        write_uint32(f, constant_stringtable_start - trk1_start)
        
        # RGBA data starts 
        for data_start in data_starts:
            write_uint32(f, data_start - trk1_start)

