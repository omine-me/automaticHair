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
else:
    from . import main
    from . import hairClass
    from . import utils
    from . import update

import bpy
from bpy.props import (
    # IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    # BoolProperty,
)

# メニューを構築する関数
# def menu_fn(self, context):
#     self.layout.separator()
#     self.layout.operator(main.AUTOHAIR_OT_New.bl_idname)
#     self.layout.operator(main.AUTOHAIR_OT_Unlink.bl_idname)

def initProps():
    scene = bpy.types.Scene
    scene.hsysTar = None
    scene.hsysCtrl = hairClass.HairCtrlSystem()
    scene.autoHairRadius = FloatProperty(
        name="Radius",
        description="Children's radius",
        default=1.0,
        min=0.0,
        update=update.setRadius
    )

def delProps():
    scene = bpy.types.Scene
    del scene.autoHairRadius
    del scene.hsysCtrl
    del scene.hsysTar

classes = [
    main.AUTOHAIR_OT_New,
    main.AUTOHAIR_OT_Unlink,
    main.AUTOHAIR_OT_Translate,
    main.AUTOHAIR_PT_Menu
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