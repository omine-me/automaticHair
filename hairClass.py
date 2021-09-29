import bpy#, sys
import numpy as np
# sys.path.append("C:/Users/omine/Documents/programs/sourceTxts")
from . import utils

class ParKey:
    def __init__(self):
        self.radius = 1.0
        self.rot = [1., 0, 0, 0]

class Child:
    def __init__(self, parent, child, psys):
        self.par = parent
        self.num = child
        self.rootDiff = psys.particles[child].hair_keys[0].co - psys.particles[parent].hair_keys[0].co

class Parent:
    def __init__(self, parAndChilds, psys):
        self.flat = 0.
        self.num = parAndChilds[0]
        self.childNum = parAndChilds[1:]
        self.childs = []
        self.keys = []
        for i in range(psys.settings.hair_step+1):
            self.keys.append(ParKey())
        for i in range(len(parAndChilds)-1):
            self.childs.append(Child(parAndChilds[0], parAndChilds[i+1], psys))

class HairCtrlSystem:
    def __init__(self, parent=None, obj=None):
        if parent is not None:
            self.tarObj = obj
            self.parentNum = parent
            self.parents = []
            C = bpy.context

            parChildCorr = np.full((len(parent), 10), -1) #10 is tmp, so diferrent num is fine
            parChildCorr[:,0] = parent #array's first column is for parent

            C.tool_settings.particle_edit.display_step = 7
            C.tool_settings.particle_edit.use_preserve_length = False

            bpy.ops.object.particle_system_add()
            psys = C.active_object.particle_systems.active
            psys.name = "AutoHairTarget"
            psys.settings.name = "AutoHairTargetParticleSettings"
            psys.settings.type = "HAIR"
            psys.settings.count = 100
            psys.settings.hair_step = 9#49
            psys.settings.display_step = 5
            targetName = C.active_object.name
            #active is changed to duplicated obj
            bpy.ops.object.duplicate_move()
            C.active_object.name = targetName + "(AutoHairControl)"
            self.ctrlObj = C.active_object
            bpy.ops.transform.translate(value=(-3,0,0))
            bpy.ops.object.particle_system_remove()
            bpy.ops.object.particle_system_add()
            psys = C.active_object.particle_systems.active
            psys.name = "AutoHairControl"
            self.psysName = psys.name
            psys.settings.name = "AutoHairControlParticleSettings"
            psys.settings.type = "HAIR"
            psys.settings.count = 1
            psys.settings.hair_step = 9

            bpy.types.Scene.hsysTar = HairTarSystem(C.active_object.name, psys.name)


            for i in range(C.scene.hsysTar.psys.settings.count):
                if not (i in parent):
                    parNumIdx = self._getClosestParNum(i)
                    if parChildCorr[parNumIdx, -1] != -1:
                        parChildCorr = np.append(parChildCorr, np.full([len(parent),1],-1), axis=1)

                    parChildCorr[parNumIdx, parChildCorr[parNumIdx,:].argmin()] = i
            
            self._setDepsgpaph()
            for i in range(len(parent)):
                self.parents.append(Parent(parChildCorr[i, :], self.psys))

            
    
    def _setDepsgpaph(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        bpy.context.view_layer.objects.active = self.ctrlObj
        bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(self.psysName)
        if bpy.context.object.mode != "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        eobj = self.ctrlObj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        self.psys = eobj.particle_systems[self.psysName]

    def _getClosestParNum(self, child):
        childPos = bpy.context.scene.hsysTar.psys.particles[child].hair_keys[0].co
        
        minDistance = 99999
        shortestParIdx = -1
        for i in range(len(self.parentNum)):
            parPos = bpy.context.scene.hsysTar.psys.particles[self.parentNum[i]].hair_keys[0].co
            distance = abs(childPos[0] - parPos[0]) + abs(childPos[1] - parPos[1]) + abs(childPos[2] - parPos[2])
            
            if distance < minDistance:
                minDistance = distance
                shortestParIdx = i
        
        return shortestParIdx
    
    def setArrayedChild(self):
        for p in self.parents:
            prevTan = np.array([0., 0., 0.])
            for s in range(self.psys.settings.hair_step+1):
                prevTan = self._setKeyRotation(p, s, prevTan)
            p.keys[-1].rot = p.keys[-2].rot #set last keys
            self._offsetChild(p)
    
    def getSelected(self):
        bpy.ops.particle.selected()
        s = {}
        for i in range(self.psys.settings.count):
            for j in range(self.psys.settings.hair_step+1):
                if bpy.context.active_object.particle_systems.active.particles[i].hair_keys[j].is_selected:
                    s.setdefault("p"+str(i),[]).append(j)
        return s
    
    def _setKeyRotation(self, p, s, prevTan):
        if s == 0:
            p.keys[0].rot = [1, 0, 0, 0]
            prevTan = np.array([0., 0., 0.])
        elif s == 1:
            prevTan = utils.sub_norm_v3_v3v3(self.psys.particles[p.num].hair_keys[1].co, self.psys.particles[p.num].hair_keys[0].co)
            p.keys[1].rot = [1, 0, 0, 0]
        else:
            tan = utils.sub_norm_v3_v3v3(self.psys.particles[p.num].hair_keys[s].co, self.psys.particles[p.num].hair_keys[s-1].co)
            cosangle = np.dot(tan, prevTan)

            if (cosangle > 0.999999):
                p.keys[s-1].rot = p.keys[s-2].rot
            else:
                angle = np.arccos(cosangle)
                norm = utils.norm_v3_v3(np.cross(prevTan, tan))
                q = utils.axis_angle_to_quat(norm, angle)
                p.keys[s-1].rot = utils.mul_qt_qtqt(q, p.keys[s-2].rot)
            
            prevTan = tan
        return prevTan

    def _offsetChild(self, p):
        print(p)
        bpy.context.scene.hsysTar._setDepsgpaph()
        for c in p.childs:
            # print(p.keys[1].radius)
            for s in range(1, bpy.context.scene.hsysTar.psys.settings.hair_step+1):
                # print("\n")
                # print(c.rootDiff, p.keys[s].radius)
                co = utils.mul_v3_v3s1(c.rootDiff, p.keys[s].radius)
                # print(co)
                co[2] *= p.flat
                co = utils.mul_v3_qtv3(p.keys[s].rot, co)
                # print(co)
                bpy.context.scene.hsysTar.psys.particles[c.num].hair_keys[s].co = self.psys.particles[p.num].hair_keys[s].co + co

class HairTarSystem:
    def __init__(self, objName, psysName):
        self.obj = bpy.data.objects[objName]
        self.psysName = psysName
        bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(psysName)
        if bpy.context.object.mode != "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        eobj = bpy.context.active_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
        self.psys = eobj.particle_systems[psysName]
    
    def _setDepsgpaph(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        bpy.context.view_layer.objects.active = self.obj
        bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(self.psysName)
        if bpy.context.object.mode != "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        eobj = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        self.psys = eobj.particle_systems[self.psysName]