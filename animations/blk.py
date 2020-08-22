import struct 
from collections import OrderedDict

from animations.general_animation import *
from animations.general_animation import basic_animation
import animations.general_animation as j3d

BLKFILEMAGIC = b"J3D1blk1"

class bone_entry(object):
    def __init__(self, time, value, tangentIn = 0, tangentOut=None):
        self.time = time
        self.value = value
        self.tangentIn = 0
        self.tangentOut = 0
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
            return cls(0.0, valarray[offset+index], 0.0, 0.0)
            
        
        else:
            #print("TanType:", tanType)
            #print(len(valarray), offset+index*4)
            
            if tanType == 0:
                return cls(valarray[offset + index*3], valarray[offset + index*3 + 1], valarray[offset + index*3 + 2])
            elif tanType == 1:
                return cls(valarray[offset + index*4], valarray[offset + index*4 + 1], valarray[offset + index*4 + 2], valarray[offset + index*4 + 3])
            else:
                raise RuntimeError("unknown tangent type: {0}".format(tanType))
    def serialize(self):
        return [self.time, self.value, self.tangentIn, self.tangentOut]
        
    def __repr__(self):
        return "Time: {0}, Val: {1}, TanIn: {2}, TanOut: {3}".format(self.time, self.value, self.tangentIn, self.tangentOut).__repr__()

class bone_anim(object):
    def __init__(self):
        self.scale = {"X": [], "Y": [], "Z": []}
        self.rotation = {"X": [], "Y": [], "Z": []}
        self.translation = {"X": [], "Y": [], "Z": []}
        
        self._scale_offsets = {}
        self._rot_offsets = {}
        self._translation_offsets = {}


    def add_scale(self, axis, comp):
        self.scale[axis].append(comp)
    
    def add_rotation(self, axis, comp):
        self.rotation[axis].append(comp)
        
    def add_translation(self, axis, comp):
        self.translation[axis].append(comp)
        
    def _set_scale_offsets(self, axis, val):
        self._scale_offsets[axis] = val

    def _set_rot_offsets(self, axis, val):
        self._rot_offsets[axis] = val

    def _set_translation_offsets(self, axis, val):
        self._translation_offsets[axis] = val

class bck(j3d.basic_animation):
    def __init__(self, loop_mode, anglescale, duration):
        self.loop_mode = loop_mode
        self.anglescale = anglescale
        self.duration = duration
        
        self.animations = []
    
    @classmethod
    def from_anim(cls, f):
        size = j3d.read_uint32(f)
        
        sectioncount = j3d.read_uint32(f)
        assert sectioncount == 1
        
        svr_data = f.read(16)
        
        clk_start = f.tell()
        clk_magic = f.read(4) #clk1
        clk_size = j3d.read_uint32(f)
        
        loop_mode = j3d.read_uint8(f)
        angle_scale = j3d.read_sint8(f) 
        rotscale = (2.0**angle_scale) * (180.0 / 32768.0);
        duration = j3d.read_uint16(f)
        blk = cls(loop_mode, angle_scale, duration)
        
        unk1_count = read_uint16(f)
        unk2_count = read_uint16(f)
        
        
        unk1_offset = read_uint32(f) + clk_start
        unk2_offset = read_uint32(f) + clk_start

        
        # Read scales 
        scales = []
        f.seek(scale_offset)
        for i in range(scale_count):
            scales.append(read_float(f))
        
        # Read unknown floats
        floats = []
        f.seek(unk2_offset)
        for i in range(unk2_count):
            rotations.append(read_float(f))
        
        
        
        
        
        f.seek(bone_offset)
        for i in range(bone_count):
            values = struct.unpack(">"+"H"*27, f.read(0x36))
            
            x_scale, x_rot, x_trans = values[:3], values[3:6], values[6:9]
            y_scale, y_rot, y_trans = values[9:12], values[12:15], values[15:18]
            z_scale, z_rot, z_trans = values[18:21], values[21:24], values[24:27]
            
            bone_animation = bone_anim()
            
            for scale, axis in ((x_scale, "X"), (y_scale, "Y"), (z_scale, "Z")):
                count, offset, tan_type = scale 
                for j in range(count):
                    comp = bone_entry.from_array(offset, j, count, scales, tan_type)
                    bone_animation.add_scale(axis, comp)
                    #print(comp)
            
            for rotation, axis in ((x_rot, "X"), (y_rot, "Y"), (z_rot, "Z")):
                count, offset, tan_type = rotation 
                for j in range(count):
                    comp = bone_entry.from_array(offset, j, count, rotations, tan_type)
                    comp.convert_rotation(rotscale)
                    bone_animation.add_rotation(axis, comp)
                    #print(comp)
                    
            for translation, axis in ((x_trans, "X"), (y_trans, "Y"), (z_trans, "Z")):
                count, offset, tan_type = translation
                for j in range(count):
                    comp = bone_entry.from_array(offset, j, count, trans, tan_type)
                    bone_animation.add_translation(axis, comp)
                    #print(comp)
                    
            bck.animations.append(bone_animation)
        return bck
    def get_children_names(self):
        joints = []
        for i in range( len( self.animations )):
            joints.append("Joint " + str(i) )
        return joints
            
    def get_loading_information(self):
        info = []
        info.append( [ "Loop Mode:", self.loop_mode, "Angle Scale:", self.anglescale, "Duration:", self.duration] )
        info.append( ["Joint Number", "Component"])
        
        keyframes_dictionary = {}
        keyframes_dictionary[0] = []
        
        i = len( info ) 
        
        count = 0
        
        for anim in self.animations:
            info.append( ["Joint " + str(count)] )
            things = ["Scale X:", "Scale Y:", "Scale Z:", "Rotation X:", "Rotation Y:", "Rotation Z:",
                "Translation X:", "Translation Y:", "Translation Z:"]
            
            for j in range (len ( things ) ):    
                comp = things[j]
                if j == 0:
                    info[i].append(comp)
                else:
                    info.append( ["", comp] )
                
                comp_dict = {}
                if comp[0:1] == "S":
                    comp_dict = anim.scale
                elif comp[0:1] == "R":
                    comp_dict = anim.rotation
                else: 
                    comp_dict = anim.translation
                    

                array = comp_dict[ comp[-2:-1] ]
                
                #print(array)                          
                 
                
                keyframes_dictionary = j3d.combine_dicts(array, keyframes_dictionary)
            i = len(info)
            
            count += 1
            
        write_values(info, keyframes_dictionary, 1)
        return info  
           
    @classmethod
    def from_table(cls, f, info):
        bck = cls(int(info[0][1]), int(info[0][3]), int(info[0][5]))
        
        keyframes = []
        
        for i in range(2, len( info[1] ) ):
            if info[1][i] != "":
                text = info[1][i][6:]
                text = int(text)
                keyframes.append(text)
        
        print("keyframes")
        print (keyframes)
        
        for i in range( int( len(info) / 9 )   ): #for each material
            line = 9 * i + 2
            current_anim = bone_anim()
            
            for j in range(9):  #for each of thing in scale/rot/trans x/y/z/       
                xyz = "XYZ"
                xyz = xyz[j%3: j%3 + 1]
                              
                for k in range(2, len(info[line + j])): #for each keyframe
                    if info[line + j][k] != "":
                        comp = bone_entry( keyframes[k-2], float(info[line + j][k]))
                                       
                        if j < 3:
                            current_anim.add_scale(xyz, comp)
                            #print("scale " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
                        elif j < 6:
                            current_anim.add_rotation(xyz, comp)
                            #print("rot " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
                        else:
                            current_anim.add_translation(xyz, comp)
                            #print("trans " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
            
             #calculate tangents
            for j in range(9):
                xyz = "XYZ"
                xyz = xyz[j%3: j%3 + 1]
                
                if j < 3:
                    current_anim.scale[xyz] = j3d.make_tangents(current_anim.scale[xyz])
                if j < 6:
                    current_anim.rotation[xyz] = j3d.make_tangents(current_anim.rotation[xyz])
                else:
                    current_anim.translation[xyz] = j3d.make_tangents(current_anim.translation[xyz])
            
            bck.animations.append(current_anim)
        with open(f, "wb") as f:
            bck.write_bck(f)
            f.close()
            
    def write_bck(self, f):
        f.write(BCKFILEMAGIC)
        filesize_offset = f.tell()
        f.write(b"ABCD") # Placeholder for file size
        j3d.write_uint32(f, 1) # Always a section count of 1
        f.write(b"\xFF"*16)
        
        clk1_start = f.tell()
        f.write(b"clk1")
        
        ttk1_size_offset = f.tell()
        f.write(b"EFGH")  # Placeholder for ttk1 size
        j3d.write_uint8(f, self.loop_mode)
        j3d.write_sint8(f, self.anglescale)
        
        rotscale = (2.0**self.anglescale)*(180.0 / 32768.0)
        
        j3d.write_uint16(f, self.duration)
        
        j3d.write_uint16(f, len( self.animations ))
        
        #0x30        
      
        count_offset = f.tell()
        f.write(b"1+1=11")  # Placeholder for scale, rotation and translation count
        
        data_offsets = f.tell()
        f.write(b"toadettebestgirl") #placeholder for offsets
        
        write_padding(f, multiple=32)
        bone_anim_start = f.tell()
        
        f.write(b"\x00"*(0x36*len(self.animations))) #placeholder for stuff
        
        write_padding(f, multiple=32)
        
        all_scales = []
        all_rotations = []
        all_translations = []
        for anim in self.animations:
            for axis in "XYZ":
                # Set up offset for scale
                if len(anim.scale[axis]) == 1:
                    sequence = [anim.scale[axis][0].value]
                else:
                    sequence = []
                    for comp in anim.scale[axis]:
                        sequence.append(comp.time)
                        sequence.append(comp.value)
                        sequence.append(comp.tangentIn)
                        sequence.append(comp.tangentOut)
                    
                offset = j3d.find_sequence(all_scales,sequence)
                if offset == -1:
                    offset = len(all_scales)
                    all_scales.extend(sequence)
                    
                anim._set_scale_offsets(axis, offset)

                # Set up offset for rotation
                if len(anim.rotation[axis]) == 1:
                    comp = anim.rotation[axis][0]
                    #angle = ((comp.value+180) % 360) - 180
                    sequence = [comp.value/rotscale]
                    print("seq", sequence)
                else:
                    sequence = []
                    for comp in anim.rotation[axis]:
                        #angle = ((comp.value+180) % 360) - 180
                        sequence.append(comp.time)
                        sequence.append(comp.value/rotscale)
                        sequence.append(comp.tangentIn/rotscale)
                        sequence.append(comp.tangentOut/rotscale)
                    print("seq", sequence)
                offset = j3d.find_sequence(all_rotations, sequence)
                if offset == -1:
                    offset = len(all_rotations)
                    all_rotations.extend(sequence)
                anim._set_rot_offsets(axis, offset)

                # Set up offset for translation
                if len(anim.translation[axis]) == 1:
                    sequence = [anim.translation[axis][0].value]
                else:
                    sequence = []
                    for comp in anim.translation[axis]:
                        sequence.append(comp.time)
                        sequence.append(comp.value)
                        sequence.append(comp.tangentIn)
                        sequence.append(comp.tangentOut)
                    
                offset = j3d.find_sequence(all_translations, sequence)
                if offset == -1:
                    offset = len(all_translations)
                    all_translations.extend(sequence)
                anim._set_translation_offsets(axis, offset)
     
                

        scale_start = f.tell()
        for val in all_scales:
            write_float(f, val)

        j3d.write_padding(f, 32)

        rotations_start = f.tell()
        for val in all_rotations:

            j3d.write_sint16(f, int(val))

        j3d.write_padding(f, 32)

        translations_start = f.tell()
        for val in all_translations:
            #print(val)
            write_float(f, val)

        j3d.write_padding(f, 32)

        total_size = f.tell()

        f.seek(bone_anim_start)
        for anim in self.animations:
            for axis in "XYZ":
                j3d.write_uint16(f, len(anim.scale[axis])) # Scale count for this animation
                j3d.write_uint16(f, anim._scale_offsets[axis]) # Offset into scales
                j3d.write_uint16(f, 1) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut


                j3d.write_uint16(f, len(anim.rotation[axis])) # Rotation count for this animation
                j3d.write_uint16(f, anim._rot_offsets[axis]) # Offset into rotations
                j3d.write_uint16(f, 1) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut


                j3d.write_uint16(f, len(anim.translation[axis])) # Translation count for this animation
                j3d.write_uint16(f, anim._translation_offsets[axis])# offset into translations
                j3d.write_uint16(f, 1) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut

        

        # Fill in all the placeholder values
        f.seek(filesize_offset)
        j3d.write_uint32(f, total_size)

        f.seek(ttk1_size_offset)
        j3d.write_uint32(f, total_size - clk1_start)

        f.seek(count_offset)
        j3d.write_uint16(f, len(all_scales))
        j3d.write_uint16(f, len(all_rotations))
        j3d.write_uint16(f, len(all_translations))
        # Next come the section offsets

        j3d.write_uint32(f, bone_anim_start     - clk1_start)
        j3d.write_uint32(f, scale_start         - clk1_start)
        j3d.write_uint32(f, rotations_start     - clk1_start)
        j3d.write_uint32(f, translations_start  - clk1_start)