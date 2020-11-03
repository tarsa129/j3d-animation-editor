import struct 
from collections import OrderedDict

from animations.general_animation import *
from animations.general_animation import basic_animation
import animations.general_animation as j3d

BLAFILEMAGIC = b"J3D1bla1"

class cluster_anim(object):
    def __init__(self):
        self.seq = []

class bla(j3d.basic_animation):
    def __init__(self, loop_mode, duration):
        self.loop_mode = loop_mode
        self.anglescale = -1
        self.duration = duration
        
        self.animations = []
    
    @classmethod
    def from_anim(cls, f):
        size = j3d.read_uint32(f)
        
        sectioncount = j3d.read_uint32(f)
        assert sectioncount == 1
        
        svr_data = f.read(16)
        
        clf_start = f.tell()
        clf_magic = f.read(4) #clf1
        clf_size = j3d.read_uint32(f)
        
        loop_mode = j3d.read_uint8(f)
        j3d.read_uint8(f)
        
        duration = j3d.read_uint16(f)
        bla = cls(loop_mode, duration)

        cluster_count = read_uint16(f) * 2
        scales_count = read_uint16(f)      
        
        print(cluster_count)
        print(scales_count)
        
        cluster_offset = read_uint32(f) + clf_start
        scales_offset = read_uint32(f) + clf_start

        # Read floats
        scales = []
        f.seek(scales_offset)
        for i in range(scales_count):

            scales.append(read_float(f))      

        # Read clusters
        
        f.seek(cluster_offset)
        for i in range(cluster_count):
            new_anim = cluster_anim()
            
            clus_durati = j3d.read_uint16(f)
            clus_offset = j3d.read_uint16(f)
            for j in range( clus_durati ):
                new_anim.seq.append( scales[j + clus_offset] ) 
            
            bla.animations.append(new_anim)
       
        return bla
    def get_children_names(self):
        joints = []
        for i in range( len( self.animations )):
            joints.append("Cluster " + str(i) )
        return joints
            
    def get_loading_information(self):
        info = []
        info.append( [ "Loop Mode:", self.loop_mode, "Duration:", self.duration] )
        info.append( ["Cluster Number", "Duration"])
        
        for i in range(self.duration):
            info[1].append("Frame " + str(i) )
        
        i = len( info ) 
        
        count = 0
        
        for anim in self.animations:
            info.append( ["Cluster " + str(count), len(anim.seq)] )
            
            for j in range (len ( anim.seq) ):    
                info[i].append( anim.seq[j] )
            
            i = len(info)
            
            count += 1
            
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
        
        clf1_start = f.tell()
        f.write(b"clf1")
        
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
        j3d.write_uint32(f, total_size - clf1_start)

        f.seek(count_offset)
        j3d.write_uint16(f, len(all_scales))
        j3d.write_uint16(f, len(all_rotations))
        j3d.write_uint16(f, len(all_translations))
        # Next come the section offsets

        j3d.write_uint32(f, bone_anim_start     - clf1_start)
        j3d.write_uint32(f, scale_start         - clf1_start)
        j3d.write_uint32(f, rotations_start     - clf1_start)
        j3d.write_uint32(f, translations_start  - clf1_start)