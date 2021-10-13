import bpy
import numpy as np
from . import utils
from .hairClass import *

"""
data structure:
isCtrl, roundness, 1posX, 1posY, 1posZ, 1radius, 1random, 1braid, 1amp, 1freq, ...9freq,
...*haircount
"""

def save(path):
    # print("aaa")
    # print(a,b,c)
    hc = bpy.context.scene.hsysCtrl
    ctrlHair = hc.ctrlHair
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
    # obj = importBaseObj()
    data = np.load(path)
    data = data["arr_0"]
    parent = []
    for idx, c in enumerate(data[:,0]):
        if c:
            parent.append(idx)

    bpy.types.Scene.hsysCtrl = HairCtrlSystem(parent, utils.importBaseObj())
    bpy.context.scene.hsysCtrl.setArrayedChild()