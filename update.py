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
        for c in k:
            # print(p, c)
            hsys.ctrlHair[p].keys[c].radius = context.scene.autoHairRadius
        # print(hsys.ctrlHair[p].keys[1].co)
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setRandom(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        for c in k:
            hsys.ctrlHair[p].keys[c].random = context.scene.autoHairRandom
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setRoundness(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        hsys.ctrlHair[p].roundness = context.scene.autoHairRoundness
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setBraid(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        for c in k:
            hsys.ctrlHair[p].keys[c].braid = context.scene.autoHairBraid
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setAmp(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        for c in k:
            hsys.ctrlHair[p].keys[c].amp = context.scene.autoHairAmp
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
        utils.particleEditNotify()
        hsys._particleEditMode()
        # hsys._setDepsgpaph()

def setFreq(self, context):
    hsys = context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    # hsys._setDepsgpaph()
    for p, k in selected.items():
        for c in k:
            hsys.ctrlHair[p].keys[c].freq = context.scene.autoHairFreq
        context.scene.hsysTar._offsetChild(hsys.ctrlHair[p])
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
        hsys.ctrlHair[p].isCtrl = isAddition
        if isAddition:
            if not hsys.ctrlHair[p].keys:
                for i in range(hsys.psys.settings.hair_step+1):
                    hsys.ctrlHair[p].keys.append(hairClass.Key(hsys.psys.particles[p].hair_keys[0].co + mathutils.Vector((0,0,.1*i))))
            for i in range(hsys.psys.settings.hair_step+1):
                hsys.psys.particles[p].hair_keys[i].co = hsys.ctrlHair[p].keys[i].co
                print(hsys.psys.particles[p].hair_keys[i].co)
        else:
            for i in range(hsys.psys.settings.hair_step+1):
                hsys.psys.particles[p].hair_keys[i].co = hsys.psys.particles[p].hair_keys[0].co
        utils.particleEditNotify()
        hsys.updateCtrlHair(hsys.ctrlHair[p])
        hsys._particleEditMode()
        hsys._setDepsgpaph()
    hsys.setArrayedChild()