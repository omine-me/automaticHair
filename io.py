import bpy, mathutils, struct
import numpy as np
from . import utils, const
from .hairClass import *
import datetime

"""
data structure:
isCtrl, roundness, 1posX, 1posY, 1posZ, 1radius, 1random, 1braid, 1amp, 1freq, ...9freq,\n
...*haircount
"""

def save(path):
    hc = bpy.context.scene.hsysCtrl
    ctrlHair = hc.ctrlHair
    hc._particleEditMode()
    hc._setDepsgpaph()
    # hairCount , 2 + (3 + 5) * hairStep
    data = np.zeros((hc.psys.settings.count, 2 + (3 + 5) * (hc.psys.settings.hair_step+1)))

    for i in range(hc.psys.settings.count):
        if ctrlHair[i].isCtrl:
            tmp1=[float(ctrlHair[i].isCtrl), \
                ctrlHair[i].roundness]
            # tmp2=[i for i in ctrlHair[i]]
            tmp2=[[j.co[0], j.co[1], j.co[2], j.radius, j.random, j.braid, j.amp, j.freq] for j in ctrlHair[i].keys[:]]
            # if braid is 0, amp and freq wiil be 0 to clean data
            for l in tmp2:
                if l[5] == 0:
                    l[6] = 0.
                    l[7] = 0.
            tmp2 = sum(tmp2, [])
            # print(tmp1+tmp2)
            data[i,:] = tmp1 + tmp2
   
    np.savez_compressed(path, data)

def load(path):
    data = np.load(path)
    data = data["arr_0"]
    parent = []
    for idx, c in enumerate(data[:,0]):
        if c:
            parent.append(idx)
        
    # print(parent)
    bpy.types.Scene.hsysCtrl = HairCtrlSystem(parent, utils.importBaseObj())
    for i in range(const.DEFAULTHAIRNUM):
        c = bpy.types.Scene.hsysCtrl.ctrlHair[i]
        c.roundness = data[i,1]
        for idx, k in enumerate(c.keys[:]):
            t = idx*8
            k.co = mathutils.Vector(data[i,2+t:5+t])
            k.radius = data[i,5+t] #5,13,21
            k.random = data[i,6+t]
            k.braid = data[i,7+t]
            k.amp = data[i,8+t]
            k.freq = data[i,9+t]
    hsysCtrl = bpy.context.scene.hsysCtrl
    hsysCtrl._particleEditMode()
    hsysCtrl._setDepsgpaph()
    for i in hsysCtrl.parentNum:
        row=data[i,:]
        for j in range(1,hsysCtrl.hairStep):
            t = j*8
            hsysCtrl.psys.particles[i].hair_keys[j].co = row[2+t:5+t]
    utils.particleEditNotify()
    hsysCtrl.setArrayedChild()

def load_data_file(path):
    def hex_to_float(s):
        global struct
        return struct.unpack('<f', s)[0]
    ### step1 read valid strands number first ###
    file = open(path, "rb")

    current_num = 0 #location in data array
    num_of_strand = 0

    data = file.read()

    #num_of_strand = int.from_bytes(data[0:4], "little") # == 10000
    current_num += 4

    parents = []
    #get hair count
    for i in range(const.DEFAULTHAIRNUM):
        num_of_vertices = int.from_bytes(data[current_num:current_num+4], "little")
        current_num += 4
        if num_of_vertices == 1:
            current_num += 12
            continue
        # for j in range(num_of_vertices):
        current_num += 12 * num_of_vertices
        parents.append(i)
        num_of_strand += 1

    file.close()

    print("end hair count check",datetime.datetime.now())

    bpy.types.Scene.hsysCtrl = HairCtrlSystem(parents, utils.importBaseObj(), isFromData=True)
    hsysCtrl = bpy.context.scene.hsysCtrl
    # hsysCtrl._particleEditMode()
    hsysCtrl._setDepsgpaph()
    print("end ctrlhair init",datetime.datetime.now())

    current_num = 0 #reset location in data array
    num_of_strand = 0
    #num_of_strand = int.from_bytes(data[0:4], "little")
    current_num += 4
    
    #set positions
    psys = hsysCtrl.psys
    for i in range(const.DEFAULTHAIRNUM):
        c = bpy.types.Scene.hsysCtrl.ctrlHair[i]
        num_of_vertices = int.from_bytes(data[current_num:current_num+4], "little")
        current_num += 4
        parti = psys.particles[i]
        if num_of_vertices != 100:
            current_num += 12
            for k in range(100):
                parti.hair_keys[k].co = parti.hair_keys[0].co
            continue
        # for k in c.keys[1:]:
        for k in range(100):
            # t = idx*8
            parti.hair_keys[k].co = mathutils.Vector((hex_to_float(data[current_num:current_num+4]), -hex_to_float(data[current_num+8:current_num+12]), hex_to_float(data[current_num+4:current_num+8])))
            # k.co = mathutils.Vector((hex_to_float(data[current_num:current_num+4]), -hex_to_float(data[current_num+8:current_num+12]), hex_to_float(data[current_num+4:current_num+8])))
            current_num += 12
    print("end ctrl hair set",datetime.datetime.now())
    utils.particleEditNotify()
    hsysCtrl.updatePos()
    print("end load",datetime.datetime.now())