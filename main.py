import bpy
import numpy as np
from . import utils
from .hairClass import *
from bpy.props import (
    # IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    BoolProperty,
)

class AUTOHAIR_OT_New(bpy.types.Operator):

    bl_idname = "autohair.new"
    bl_label = "New AutoHair"
    bl_description = "New Hair Particles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.types.Scene.hsysCtrl = HairCtrlSystem([0], bpy.context.active_object)
        bpy.context.scene.hsysCtrl.setArrayedChild()

        return {'FINISHED'}

class AUTOHAIR_OT_Load(bpy.types.Operator):

    bl_idname = "autohair.load"
    bl_label = "Load"
    bl_description = "Load MAT File"
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

class AUTOHAIR_OT_Save(bpy.types.Operator):

    bl_idname = "autohair.save"
    bl_label = "Save"
    bl_description = "Save MAT File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        return {'FINISHED'}

class AUTOHAIR_OT_Translate(bpy.types.Operator):

    bl_idname = "autohair.translate"
    bl_label = "Update Position"
    bl_description = "Update positions of target hair"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.hsysCtrl.updatePos()
        # print(context.scene.hsysCtrl.ctrlHair[0].keys[1].co)
        return {'FINISHED'}

class AUTOHAIRPanel:
    bl_space_type = 'VIEW_3D'           # パネルを登録するスペース
    bl_region_type = 'UI'               # パネルを登録するリージョン
    bl_category = "AutoHair"        # パネルを登録するタブ名

class AUTOHAIR_PT_Menu(AUTOHAIRPanel, bpy.types.Panel):
    bl_label = "AutoHair"         # パネルのヘッダに表示される文字列
    bl_idname = "AUTOHAIR_PT_Menu"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Start from here:")
        layout.operator(AUTOHAIR_OT_New.bl_idname)
        layout.operator(AUTOHAIR_OT_Load.bl_idname)
        layout.operator(AUTOHAIR_OT_Unlink.bl_idname)
        layout.separator()
        layout.operator(AUTOHAIR_OT_Save.bl_idname)

class AUTOHAIR_PT_Menu2(AUTOHAIRPanel, bpy.types.Panel):
    bl_parent_id = "AUTOHAIR_PT_Menu"
    bl_label = "Hair Properties"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "autoHairIsCtrl")
        layout.prop(scene, "autoHairRoundness")

class AUTOHAIR_PT_Menu3(AUTOHAIRPanel, bpy.types.Panel):
    bl_parent_id = "AUTOHAIR_PT_Menu"
    bl_label = "Key Properties"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator(AUTOHAIR_OT_Translate.bl_idname)
        layout.prop(scene, "autoHairRadius")
        layout.prop(scene, "autoHairRandom")
        layout.prop(scene, "autoHairBraid")
        layout.prop(scene, "autoHairAmp")
        layout.prop(scene, "autoHairFreq")
class AUTOHAIR_PT_Menu4(AUTOHAIRPanel, bpy.types.Panel):
    bl_parent_id = "AUTOHAIR_PT_Menu"
    bl_label = "Tools"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene.tool_settings.particle_edit, "use_preserve_length")
        layout.prop(scene.tool_settings.particle_edit, "use_preserve_root")