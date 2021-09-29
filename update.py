import bpy

def setRadius(self, context):
    hsys = bpy.context.scene.hsysCtrl
    hsys._setDepsgpaph()
    selected = hsys.getSelected()
    hsys._setDepsgpaph()
    for p, k in selected.items():
        pNum = int(p[1:])
        for c in k:
            # print(pNum, c)
            hsys.parents[0].keys[c].radius = context.scene.autoHairRadius
        bpy.context.scene.hsysTar._setDepsgpaph()
        hsys._offsetChild(hsys.parents[0])
        hsys._setDepsgpaph()

# def update(self, context):
