import bpy, mathutils
from . import utils, hairClass

def setRadius(self, context):
    hsys = context.scene.hsysCtrl
    # print(hsys.ctrlHair[0].keys[1].co)
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    # print(hsys.ctrlHair[0].keys[1].co)
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            # print(pNum, c)
            hsys.ctrlHair[pNum].keys[c].radius = context.scene.autoHairRadius
        # print(hsys.ctrlHair[pNum].keys[1].co)
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setRandom(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            hsys.ctrlHair[pNum].keys[c].random = context.scene.autoHairRandom
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setRoundness(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        hsys.ctrlHair[pNum].roundness = context.scene.autoHairRoundness
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setBraid(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            hsys.ctrlHair[pNum].keys[c].braid = context.scene.autoHairBraid
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setAmp(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            hsys.ctrlHair[pNum].keys[c].amp = context.scene.autoHairAmp
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setFreq(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            hsys.ctrlHair[pNum].keys[c].freq = context.scene.autoHairFreq
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[pNum])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setCtrlHair(context, isAddition):
    hsys = context.scene.hsysCtrl
    hsys._particleEditMode()
    hsys._setDepsgpaph()
    selected = hsys.getSelected() #this causes resetting depsgraph
    hsys._particleEditMode()
    hsys._setDepsgpaph()
    for p in selected.keys():
        pNum = int(p[1:])
        hsys.ctrlHair[pNum].isCtrl = isAddition
        if isAddition:
            if not hsys.ctrlHair[pNum].keys:
                for i in range(hsys.psys.settings.hair_step+1):
                    hsys.ctrlHair[pNum].keys.append(hairClass.Key(hsys.psys.particles[pNum].hair_keys[0].co + mathutils.Vector((0,0,.1*i))))
            for i in range(hsys.psys.settings.hair_step+1):
                hsys.psys.particles[pNum].hair_keys[i].co = hsys.ctrlHair[pNum].keys[i].co
                print(hsys.psys.particles[pNum].hair_keys[i].co)
        else:
            for i in range(hsys.psys.settings.hair_step+1):
                hsys.psys.particles[pNum].hair_keys[i].co = hsys.psys.particles[pNum].hair_keys[0].co
        utils.particleEditNotify()
        hsys.updateCtrlHair(hsys.ctrlHair[pNum])
        hsys._particleEditMode()
        hsys._setDepsgpaph()
    hsys.setArrayedChild()