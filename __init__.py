bl_info = {
    "name": "autoHair",
    "author": "Omine Taisei",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "3Dビューポート",
    "description": "ヘアモデリングの簡易化",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Particle"
}

if "bpy" in locals():
    import imp
    imp.reload(hairClass)
    imp.reload(main)
    imp.reload(utils)
    imp.reload(update)
    imp.reload(const)
    imp.reload(io)
else:
    from . import main
    from . import hairClass
    from . import utils
    from . import update
    from . import const
    from . import io

import bpy
from bpy.props import (
    # IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    # BoolProperty,
)

def initProps():
    scene = bpy.types.Scene
    scene.hsysTar = None
    scene.hsysCtrl = hairClass.HairCtrlSystem()
    # scene.autoHairIsCtrl = BoolProperty(
    #     name="Is Control Hair",
    #     description="Is This Hair Control",
    #     default=False,
    #     update=update.setIsCtrl
    # )
    scene.autoHairRoundness = FloatProperty(
        name="Roundness",
        description="Children's roundness",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update.setRoundness
    )
    scene.autoHairRadius = FloatProperty(
        name="Radius",
        description="Children's radius",
        default=.1,
        min=0.0,
        update=update.setRadius
    )
    scene.autoHairRandom = FloatProperty(
        name="Random",
        description="Children's randomness",
        default=1.0,
        min=0.0,
        update=update.setRandom
    )
    scene.autoHairBraid = FloatProperty(
        name="Braidness",
        description="Children's braidness",
        default=0.0,
        min=0.0,
        update=update.setBraid
    )
    scene.autoHairAmp = FloatProperty(
        name="Amplitude",
        description="Children's Amplitude",
        default=.05,
        min=0.0,
        update=update.setAmp
    )
    scene.autoHairFreq = FloatProperty(
        name="Frequency",
        description="Children's Frequency",
        default=5.,
        min=0.0,
        update=update.setFreq
    )

def delProps():
    scene = bpy.types.Scene
    del scene.autoHairRadius
    del scene.autoHairRandom
    del scene.autoHairRoundness
    del scene.autoHairBraid
    del scene.autoHairAmp
    del scene.autoHairFreq
    del scene.hsysCtrl
    del scene.hsysTar

classes = [
    main.AUTOHAIR_OT_New,
    main.AUTOHAIR_OT_Load,
    main.AUTOHAIR_OT_LoadDataFile,
    main.AUTOHAIR_OT_Save,
    main.AUTOHAIR_OT_Unlink,
    main.AUTOHAIR_OT_Translate,
    main.AUTOHAIR_OT_AddCtrlHair,
    main.AUTOHAIR_OT_RemoveCtrlHair,
    main.AUTOHAIR_PT_Menu,
    main.AUTOHAIR_PT_Menu2,
    main.AUTOHAIR_PT_Menu3,
    main.AUTOHAIR_PT_Menu4
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    initProps()
    print("AutoHair registered")


def unregister():
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)
    print("AutoHair unregistered")


if __name__ == "__main__":
    register()