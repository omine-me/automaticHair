import bpy, mathutils
import numpy as np
from . import utils
from .hairClass import *

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
    data = np.zeros((hc.psys.settings.count, 2 + (3 + 5) * (hc.psys.settings.hair_step)))

    for i in range(hc.psys.settings.count):
        if ctrlHair[i].isCtrl:
            tmp1=[float(ctrlHair[i].isCtrl), \
                ctrlHair[i].roundness]
            # tmp2=[i for i in ctrlHair[i]]
            tmp2=[[j.co[0], j.co[1], j.co[2], j.radius, j.random, j.braid, j.amp, j.freq] for j in ctrlHair[i].keys[1:]]
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

    bpy.types.Scene.hsysCtrl = HairCtrlSystem(parent, utils.importBaseObj())
    for i in range(10000):
        c = bpy.types.Scene.hsysCtrl.ctrlHair[i]
        c.roundness = data[i,1]
        for idx, k in enumerate(c.keys[1:]):
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
        for j in range(hsysCtrl.psys.settings.hair_step):
            t = j*8
            hsysCtrl.psys.particles[i].hair_keys[j+1].co = data[i,2+t:5+t]
    utils.particleEditNotify()
    hsysCtrl.setArrayedChild()