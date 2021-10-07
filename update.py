import bpy
from . import utils

def setRadius(self, context):
    hsys = context.scene.hsysCtrl
    print(hsys.ctrlHair[0].keys[1].co)
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    hsys._setDepsgpaph()
    print(hsys.ctrlHair[0].keys[1].co)
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            # print(pNum, c)
            hsys.ctrlHair[pNum].keys[c].radius = context.scene.autoHairRadius
        print(hsys.ctrlHair[pNum].keys[1].co)
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._setDepsgpaph()

def setRandom(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            hsys.ctrlHair[pNum].keys[c].random = context.scene.autoHairRandom
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._setDepsgpaph()

def setIsCtrl(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        hsys.ctrlHair[pNum].isCtrl = context.scene.autoHairIsCtrl
        if context.scene.autoHairIsCtrl:
            for i in range(hsys.psys.settings.hair_step+1):
                # hsys.ctrlHair[pNum].keys[c].co = hsys.ctrlHair[pNum].keys[0].co + (0,0,.1*c)
                hsys.psys.particles[pNum].hair_keys[i].co = hsys.ctrlHair[pNum].keys[0].co + (0,0,.5*i)
        else:
            for i in range(hsys.psys.settings.hair_step+1):
                # hsys.ctrlHair[pNum].keys[c].co = hsys.ctrlHair[pNum].keys[0].co
                hsys.psys.particles[pNum].hair_keys[i].co = hsys.ctrlHair[pNum].keys[0].co
        # context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        # utils.particleEditNotify()
        hsys._setDepsgpaph()

def setRoundness(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        hsys.ctrlHair[pNum].roundness = context.scene.autoHairRoundness
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        # utils.particleEditNotify()
        hsys._setDepsgpaph()