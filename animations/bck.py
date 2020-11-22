import struct 
from collections import OrderedDict

from animations.general_animation import *
from animations.general_animation import basic_animation
import animations.general_animation as j3d

BTKFILEMAGIC = b"J3D1bck1"

class bone_anim(object):
    def __init__(self):
        self.scale = {"X": [], "Y": [], "Z": []}
        self.rotation = {"X": [], "Y": [], "Z": []}
        self.translation = {"X": [], "Y": [], "Z": []}
        self.joint_name = ""
        
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
    def __init__(self, loop_mode, anglescale, duration, tantype = 1):
        self.loop_mode = loop_mode
        self.anglescale = anglescale
        self.duration = duration
        
        self.animations = []
    
        if tantype == 0 or tantype == 1:
            self.tan_type = tantype
        else:
            self.tan_type = 1
    
    @classmethod
    def from_anim(cls, f):
        size = j3d.read_uint32(f)
        
        sectioncount = j3d.read_uint32(f)
        assert sectioncount == 1
        
        svr_data = f.read(16)
        
        ank_start = f.tell()
        ank_magic = f.read(4) #ank1
        ank_size = j3d.read_uint32(f)
        
        loop_mode = j3d.read_uint8(f)
        angle_scale = j3d.read_sint8(f) 
        rotscale = (2.0**angle_scale) * (180.0 / 32768.0);
        duration = j3d.read_uint16(f)
        bck = cls(loop_mode, angle_scale, duration)
        
        bone_count = read_uint16(f)
        scale_count = read_uint16(f)
        rotation_count = read_uint16(f)
        trans_count = read_uint16(f)
        
        bone_offset = read_uint32(f) + ank_start
        scale_offset = read_uint32(f) + ank_start
        rotation_offset = read_uint32(f) + ank_start
        trans_offset = read_uint32(f) + ank_start
        
        # Read scales 
        scales = []
        f.seek(scale_offset)
        for i in range(scale_count):
            scales.append(read_float(f))
        
        # Read rotations
        rotations = []
        f.seek(rotation_offset)
        for i in range(rotation_count):
            rotations.append((read_sint16(f)))
        
        # Read translations 
        trans = []
        f.seek(trans_offset)
        for i in range(trans_count):
            trans.append(read_float(f))
        
        tangent_type = 0
        
        f.seek(bone_offset)
        for i in range(bone_count):
            values = struct.unpack(">"+"H"*27, f.read(0x36))
            
            x_scale, x_rot, x_trans = values[:3], values[3:6], values[6:9]
            y_scale, y_rot, y_trans = values[9:12], values[12:15], values[15:18]
            z_scale, z_rot, z_trans = values[18:21], values[21:24], values[24:27]
            
            bone_animation = bone_anim()
            
            for scale, axis in ((x_scale, "X"), (y_scale, "Y"), (z_scale, "Z")):
                count, offset, tan_type = scale 
                tangent_type = max(tan_type, tangent_type)
                for j in range(count):
                    comp = j3d.AnimComponent.from_array(offset, j, count, scales, tan_type)
                    bone_animation.add_scale(axis, comp)
                    #print(comp)
            
            for rotation, axis in ((x_rot, "X"), (y_rot, "Y"), (z_rot, "Z")):
                count, offset, tan_type = rotation 
                tangent_type = max(tan_type, tangent_type)
                for j in range(count):
                    comp = j3d.AnimComponent.from_array(offset, j, count, rotations, tan_type)
                    comp.convert_rotation(rotscale)
                    bone_animation.add_rotation(axis, comp)
                    #print(comp)
                    
            for translation, axis in ((x_trans, "X"), (y_trans, "Y"), (z_trans, "Z")):
                count, offset, tan_type = translation
                tangent_type = max(tan_type, tangent_type)
                for j in range(count):
                    comp = j3d.AnimComponent.from_array(offset, j, count, trans, tan_type)
                    bone_animation.add_translation(axis, comp)
                    #print(comp)
                    
            bck.animations.append(bone_animation)
        bck.tan_type = tangent_type
        
        return bck
    
    @classmethod
    def from_maya_anim(cls, filepath):
        lines = filepath.readlines()
        duration = int( lines[6][lines[6].find(" "): lines[6].find(";")] )
        #duration -= int( lines[5][lines[5].find(" "): lines[5].find(";")] )
        max = 0
        print (duration)
        i = 7
        bck = cls(1, 1, duration)
        
        current_bone = lines[i].split()[3]
        
        #iterate through all the lines
        while ( i < len(lines) ):
        
            # make a new bone
            new_bone_name = lines[i].split()[3]
            current_bone = new_bone_name
            new_bone = bone_anim()
            new_bone.joint_name = new_bone_name
            bck.animations.append(new_bone)
            
            # while it is the same bone animation
            while(new_bone_name == current_bone):
                current_bone = new_bone_name
                
                #jump to keys for the entry  
                
                values = lines[i].split()
                thing = values[2]
                

                i += 8     
   
                #read the keyframes
                while( not "}" in lines[i]):
                    values = lines[i].split()
                    
                    new_entry = j3d.AnimComponent(int(values[0]), float(values[1]))
                
                    if len(thing) == 6:
                        new_bone.add_scale( thing[-1], new_entry )
                    elif len(thing) == 7:
                        new_bone.add_rotation( thing[-1], new_entry )
                    else:
                        new_bone.add_translation( thing[-1], new_entry )                  
                    i += 1
                
                i += 2
                
                if( i < len(lines) ):
                    new_bone_name = lines[i].split()[3]
                else:
                    new_bone_name = current_bone + "asdf"
        
        for anim in bck.animations :
            for axis in {"X", "Y", "Z"} :
                if len( anim.scale[axis] ) == 0:
                    new_entry = j3d.AnimComponent(0, 1.0)
                    anim.add_scale(axis, new_entry)
                if len( anim.rotation[axis] ) == 0:
                    new_entry = j3d.AnimComponent(0, 0)
                    anim.add_rotation(axis, new_entry)
                if len( anim.translation[axis] ) == 0:
                    new_entry = j3d.AnimComponent(0, 0)
                    anim.add_translation(axis, new_entry)

        
        return bck

    
    def get_children_names(self):
        joints = []
        for i in range( len( self.animations )):
            if self.animations[i].joint_name != "":
                joints.append( self.animations[i].joint_name)
            else:
                joints.append("Joint " + str(i) )
        return joints
            
    def get_loading_information(self):
        info = []
        info.append( [ "Loop Mode:", self.loop_mode, "Angle Scale:", self.anglescale, "Duration:", self.duration, "Tan Type:", self.tan_type] )
        info.append( ["Bone Name", "Component"])
        
        keyframes_dictionary = {}
        keyframes_dictionary[0] = []
        
        i = len( info ) 
        
        count = 0
        
        for anim in self.animations:
            if anim.joint_name == "":
                info.append( ["Joint " + str(count)] )
            else:
                info.append( [anim.joint_name] )
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
    def empty_table(cls, created):
        info = []
        info.append( ["Loop_mode", "", "Angle Scale:", "", "Duration:", created[3], "Tan Type:", self.tan_type] )
        info.append( ["Joint Number", "Component"] )

        for i in range( int(created[3])):
            info[1].append("Frame " + str(i) )
        
        for i in range( int(created[1]) ):
            info.append( ["Joint " + str(i), "Scale U:"] )
            
            things = ["Scale V:", "Scale W:", "Rotation U:", "Rotation V:", "Rotation W:",
                "Translation U:", "Translation V:", "Translation W:"]
            for comp in things:
                info.append( ["", comp] )
        return info          
    
    @classmethod
    def from_table(cls, f, info):
        print(f)
        bck = cls(int(info[0][1]), int(info[0][3]), int(info[0][5]))
        
        if info[0][7] != "":
            bck.tan_type( info[0][7] )
        
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
                        try:
                            comp = j3d.AnimComponent( keyframes[k-2], float(info[line + j][k]))
                        except:
                            comp = j3d.AnimComponent( bck.duration, float(info[line + j][k]) )
                                                                   
                        if j < 3:
                            current_anim.add_scale(xyz, comp)
                            #print("scale " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
                        elif j < 6:
                            """if comp.value < -180 * bck.anglescale:
                                comp.value = comp.value + 360 * bck.anglescale
                            elif comp.value > 180 * bck.anglescale:
                                comp.value = comp.value - 360 * bck.anglescale"""
                            current_anim.add_rotation(xyz, comp)
                            #print("rot " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
                        else:
                            current_anim.add_translation(xyz, comp)
                            #print("trans " + xyz + " " + str(keyframes[k-2]) + ", " + str( float(info[line + j][k])))
            
             #calculate tangents
            """
            for j in range(9):
                xyz = "XYZ"
                xyz = xyz[j%3: j%3 + 1]
                
                if j < 3:
                    current_anim.scale[xyz] = j3d.make_tangents(current_anim.scale[xyz])
                if j < 6:
                    current_anim.rotation[xyz] = j3d.make_tangents(current_anim.rotation[xyz])
                else:
                    current_anim.translation[xyz] = j3d.make_tangents(current_anim.translation[xyz]) """
            
            bck.animations.append(current_anim)
        if f == "":
            print("no saving")
            return bck
        else:
            with open(f, "wb") as f:
                bck.write_bck(f)
                f.close()
   
    
    def write_bck(self, f):
        f.write(BCKFILEMAGIC)
        filesize_offset = f.tell()
        f.write(b"ABCD") # Placeholder for file size
        j3d.write_uint32(f, 1) # Always a section count of 1
        f.write(b"\xFF"*16)
        
        ank1_start = f.tell()
        f.write(b"ANK1")
        
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
                        if self.tan_type == 1 :
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
                    #print("seq", sequence)
                else:
                    sequence = []
                    for comp in anim.rotation[axis]:
                        #angle = ((comp.value+180) % 360) - 180
                        sequence.append(comp.time)
                        sequence.append(comp.value/rotscale)
                        sequence.append(comp.tangentIn/rotscale)
                        if self.tan_type == 1 :
                            sequence.append(comp.tangentOut/rotscale)
                    #print("seq", sequence)
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
                        if self.tan_type == 1 :
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
            
            val = int(val)
            if val <= -32767:
                val = -32767
            elif val > 32767:
                val = 32767
            
            #try:
            j3d.write_sint16(f, val )
            """except:
                print(val)"""

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
                j3d.write_uint16(f, self.tan_type) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut


                j3d.write_uint16(f, len(anim.rotation[axis])) # Rotation count for this animation
                j3d.write_uint16(f, anim._rot_offsets[axis]) # Offset into rotations
                j3d.write_uint16(f, self.tan_type) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut


                j3d.write_uint16(f, len(anim.translation[axis])) # Translation count for this animation
                j3d.write_uint16(f, anim._translation_offsets[axis])# offset into translations
                j3d.write_uint16(f, self.tan_type) # Tangent type, 0 = only TangentIn; 1 = TangentIn and TangentOut

        

        # Fill in all the placeholder values
        f.seek(filesize_offset)
        j3d.write_uint32(f, total_size)

        f.seek(ttk1_size_offset)
        j3d.write_uint32(f, total_size - ank1_start)

        f.seek(count_offset)
        j3d.write_uint16(f, len(all_scales))
        j3d.write_uint16(f, len(all_rotations))
        j3d.write_uint16(f, len(all_translations))
        # Next come the section offsets

        j3d.write_uint32(f, bone_anim_start     - ank1_start)
        j3d.write_uint32(f, scale_start         - ank1_start)
        j3d.write_uint32(f, rotations_start     - ank1_start)
        j3d.write_uint32(f, translations_start  - ank1_start)
    
    @classmethod
    def get_bck(cls, info):
        bck = cls.from_table("", info)    
        return bck
        
    