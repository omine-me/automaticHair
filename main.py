import bpy#, sys #,os
import numpy as np
# sys.path.append("C:/Users/omine/Documents/programs/sourceTxts")
from . import utils

#for reload modified script
# from importlib import reload
# reload(hairClass)
# myscript.main()
from .hairClass import *

from bpy.props import (
    # IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    # BoolProperty,
)


# bpy.ops.particle.brush_edit(stroke=[{"name":"", "location":(0, 0, 0), "mouse":(0, 0), "mouse_event":(0, 0), "pressure":0, "size":0, "pen_flip":False, "x_tilt":0, "y_tilt":0, "time":0, "is_start":False}])
#bpy.ops.particle.particle_edit_toggle()

class AUTOHAIR_OT_New(bpy.types.Operator):

    bl_idname = "autohair.new"
    bl_label = "New AutoHair"
    bl_description = "Make new AutoHair"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.types.Scene.hsysCtrl = HairCtrlSystem([0], bpy.context.active_object)
        bpy.context.scene.hsysCtrl.setArrayedChild()

        return {'FINISHED'}

class AUTOHAIR_OT_Unlink(bpy.types.Operator):

    bl_idname = "autohair.unlink"
    bl_label = "Unlink"
    bl_description = "Unlink Particle System"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        return {'FINISHED'}

# class AUTOHAIR_OT_SetRadius(bpy.types.Operator):

#     bl_idname = "autohair.set_radius"
#     bl_label = "Radius"
#     bl_description = "Set Children's Radius"
#     bl_options = {'REGISTER', 'UNDO'}

#     radius: FloatProperty(default = 1.0, options = {"HIDDEN"})

#     def execute(self, context):
#         # global hsys
#         bpy.types.Scene.hsys.setRadius(self.radius)

#         return {'FINISHED'}

class AUTOHAIR_PT_Menu(bpy.types.Panel):
    bl_label = "AutoHair"         # パネルのヘッダに表示される文字列
    bl_space_type = 'VIEW_3D'           # パネルを登録するスペース
    bl_region_type = 'UI'               # パネルを登録するリージョン
    bl_category = "AutoHair"        # パネルを登録するタブ名
    # bl_context = "objectmode"           # パネルを表示するコンテキスト

    # 本クラスの処理が実行可能かを判定する
    # @classmethod
    # def poll(cls, context):
    #     # オブジェクトが選択されているときのみメニューを表示させる
    #     for o in bpy.data.objects:
    #         if o.select_get():
    #             return True
    #     return False
    # @classmethod
    # def poll(cls, context):
    #     if(context.selected_objects):
    #         if(context.selected_objects[0].type == "MESH"):
    #             return True
    #     return False
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator(AUTOHAIR_OT_New.bl_idname)
        layout.operator(AUTOHAIR_OT_Unlink.bl_idname)
        layout.separator()
        layout.prop(scene, "autoHairRadius")

        # opProp = layout.operator(AUTOHAIR_OT_SetRadius.bl_idname)
        # opProp.radius = context.scene.autoHairRadius