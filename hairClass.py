import bpy
import numpy as np
from . import utils
import mathutils

class Key:
    def __init__(self, co):
        self.co = mathutils.Vector(co)
        self.radius = .1
        self.rot = [1., 0, 0, 0]
        self.random = 0.
        # self.braid
        # self.amp
        # self.freq

class TarHair:
    def __init__(self, ctrlHairNum, tarHairNum, psys):
        self.num = tarHairNum
        self.rootDiff = psys.particles[tarHairNum].hair_keys[0].co - psys.particles[ctrlHairNum].hair_keys[0].co

class CtrlHair:
    def __init__(self, idx, parAndChilds, psys, tarHairKeyPos):
        self.roundness = 0.
        self.isCtrl = True if idx == parAndChilds[0] else False
        # self.まとまりのrandomness
        self.ctrlNum = idx
        # self.childNum = parAndChilds[1:]
        self.tarHair = []
        self.keys = []
        for i in range(psys.settings.hair_step+1):
            self.keys.append(Key(tarHairKeyPos[i,:]))
        for i in range(len(parAndChilds)):
            self.tarHair.append(TarHair(parAndChilds[0], parAndChilds[i], psys))

class HairCtrlSystem:
    def __init__(self, parent=None, obj=None):
        if parent is not None:
            self.tarObj = obj
            self.parentNum = parent
            self.ctrlHair = []
            C = bpy.context
            pLen = len(parent)

            parChildCorr = np.full((pLen, 10), -1) #10 is tmp, so diferrent num is fine
            parChildCorr[:,0] = parent #array's first column is for parent

            C.tool_settings.particle_edit.display_step = 7
            C.tool_settings.particle_edit.use_preserve_length = False

            # bpy.ops.object.particle_system_add() #ほんとはloadする
            psys = C.active_object.particle_systems.active
            psys.name = "AutoHairTarget"
            psys.settings.name = "AutoHairTargetParticleSettings"
            psys.settings.type = "HAIR"
            # psys.settings.count = 100
            # psys.settings.hair_step = 9#49
            psys.settings.display_step = 5
            targetName = C.active_object.name

            # get parent's pos
            bpy.types.Scene.hsysTar = HairTarSystem(C.active_object, psys.name)
            tarParPos = np.empty((pLen, C.scene.hsysTar.psys.settings.hair_step+1, 3))
            C.scene.hsysTar._setDepsgpaph()
            for i in range(pLen):
                for j in range(C.scene.hsysTar.psys.settings.hair_step+1):
                    tarParPos[i,j,:] = C.scene.hsysTar.psys.particles[parent[i]].hair_keys[j].co
            
            # get child hair of each parent hair
            for i in range(C.scene.hsysTar.psys.settings.count):
                if not (i in parent):
                    parNumIdx = C.scene.hsysTar._getClosestParNum(i, parent)
                    if parChildCorr[parNumIdx, -1] != -1:
                        parChildCorr = np.append(parChildCorr, np.full([pLen,1],-1), axis=1)

                    parChildCorr[parNumIdx, parChildCorr[parNumIdx,:].argmin()] = i
            
            for i in range(pLen):
                self.ctrlHair.append(CtrlHair(i, parChildCorr[i, :], C.scene.hsysTar.psys, tarParPos[i, :, :]))
            utils.particleEditNotify()
            bpy.ops.particle.particle_edit_toggle()

            #active is changed to duplicated obj
            bpy.ops.object.duplicate_move()
            C.active_object.name = targetName + "(AutoHairControl)"
            self.ctrlObj = C.active_object
            bpy.ops.transform.translate(value=(-1,0,0))
            bpy.ops.object.particle_system_remove()
            bpy.ops.object.particle_system_add()
            self.psys = C.active_object.particle_systems.active
            self.psys.name = self.psysName = "AutoHairControl"
            self.psys.settings.name = "AutoHairControlParticleSettings"
            self.psys.settings.type = "HAIR"
            self.psys.settings.count = pLen
            self.psys.settings.hair_step = 9
            self.psys.settings.display_step = 5

            self._setDepsgpaph()
            for i in range(self.psys.settings.count):
                for j in range(self.psys.settings.hair_step+1):
                    self.psys.particles[i].hair_keys[j].co = tarParPos[i,j,:]
            utils.particleEditNotify()
            # bpy.ops.particle.particle_edit_toggle()

    def _setDepsgpaph(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        bpy.context.view_layer.objects.active = self.ctrlObj
        bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(self.psysName)
        if bpy.context.object.mode != "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        eobj = self.ctrlObj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        self.psys = eobj.particle_systems[self.psysName]

    
    def setArrayedChild(self):
        for p in self.ctrlHair:
            self._setDepsgpaph()
            prevTan = np.array([0., 0., 0.])
            # print(p.ctrlNum)
            for s in range(self.psys.settings.hair_step+1):
                # print(s)
                # self._setDepsgpaph()
                prevTan = self._setKeyRotation(p, s, prevTan)
            p.keys[-1].rot = p.keys[-2].rot #set last keys
            bpy.context.scene.hsysTar._offsetChild(p)
        # self._setDepsgpaph()
    
    def getSelected(self):
        bpy.ops.particle.selected()
        s = {}
        for i in range(self.psys.settings.count):
            for j in range(self.psys.settings.hair_step+1):
                if bpy.context.active_object.particle_systems.active.particles[i].hair_keys[j].is_selected: #use bpy.data
                    s.setdefault("p"+str(i),[]).append(j)
        return s
    
    def _setKeyRotation(self, p, s, prevTan):
        if s == 0:
            # p.keys[0].rot = [1, 0, 0, 0]
            # prevTan = np.array([0., 0., 0.])
            pass
        elif s == 1:
            prevTan = utils.sub_norm_v3_v3v3(self.psys.particles[p.ctrlNum].hair_keys[1].co, self.psys.particles[p.ctrlNum].hair_keys[0].co)
            p.keys[0].rot = [1, 0, 0, 0]
        else:
            tan = utils.sub_norm_v3_v3v3(self.psys.particles[p.ctrlNum].hair_keys[s].co, self.psys.particles[p.ctrlNum].hair_keys[s-1].co)
            # tan = utils.sub_norm_v3_v3v3(self.psys.particles[p.ctrlNum].hair_keys[s-1].co, self.psys.particles[p.ctrlNum].hair_keys[s].co)
            # print(self.psys.particles[p.ctrlNum].hair_keys[s].co, self.psys.particles[p.ctrlNum].hair_keys[s-1].co)
            cosangle = utils.dot_fl_v3v3(tan, prevTan)
            # print(cosangle)
            if (cosangle > 0.999999): #tan and prevTan are opposite
                p.keys[s-1].rot = p.keys[s-2].rot
            else:
                angle = np.arccos(cosangle)
                # print(angle)
                norm = utils.norm_v3_v3(np.cross(prevTan, tan))
                # norm = utils.norm_v3_v3(np.cross(tan, prevTan))
                # norm = utils.norm_v3_v3(tan)
                # print(norm)
                q = utils.axis_angle_to_quat(norm, angle) #when angle is 1 or -1, q = [1,0,0,0]
                # q = utils.axis_angle_to_quat(norm, .5) #when angle is 1 or -1, q = [1,0,0,0]
                # print(q)
                p.keys[s-1].rot = utils.mul_qt_qtqt(q, p.keys[s-2].rot)
                # p.keys[s-1].rot = q
                # print(utils.mul_qt_qtqt(q, p.keys[s-2].rot))
            
            prevTan = tan
        return prevTan
    
    def _setKeyPos(self):
        self._setDepsgpaph()
        for i in range(self.psys.settings.count):
            # self._setDepsgpaph()
            for j in range(self.psys.settings.hair_step+1):
                # self._setDepsgpaph()
                self.ctrlHair[i].keys[j].co = mathutils.Vector(self.psys.particles[i].hair_keys[j].co)
                # print(self.ctrlHair[i].keys[j].co,self.psys.particles[i].hair_keys[j].co)
    
    def updatePos(self):
        self._setKeyPos()
        # print(self.ctrlHair[0].keys[1].co)
        self.setArrayedChild()

class HairTarSystem:
    def __init__(self, obj, psysName):
        self.obj = obj
        self.psysName = psysName
        self.psys = obj.particle_systems.active
        # bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(psysName)
        # if bpy.context.object.mode != "PARTICLE_EDIT":
        #     bpy.ops.particle.particle_edit_toggle()
        # eobj = bpy.context.active_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
        # self.psys = eobj.particle_systems[psysName]
    
    def _setDepsgpaph(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        bpy.context.view_layer.objects.active = self.obj
        bpy.context.object.particle_systems.active_index = bpy.context.object.particle_systems.find(self.psysName)
        if bpy.context.object.mode != "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
        eobj = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        self.psys = eobj.particle_systems[self.psysName]
        bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False

    def _getClosestParNum(self, child, parents):
        childPos = bpy.context.scene.hsysTar.psys.particles[child].hair_keys[0].co
        
        minDistance = 99999
        shortestParIdx = -1
        for i in range(len(parents)):
            parPos = bpy.context.scene.hsysTar.psys.particles[parents[i]].hair_keys[0].co
            distance = abs(childPos[0] - parPos[0]) + abs(childPos[1] - parPos[1]) + abs(childPos[2] - parPos[2])
            
            if distance < minDistance:
                minDistance = distance
                shortestParIdx = i
        
        return shortestParIdx

    def _offsetChild(self, p):
        # print(p)
        bpy.context.scene.hsysTar._setDepsgpaph()
        for c in p.tarHair:
            # print(p.keys[1].radius, p.keys[1].co)
            for s in range(1, bpy.context.scene.hsysTar.psys.settings.hair_step+1):
                # print("\n")
                # print(c.rootDiff, p.keys[s].radius)
                co = utils.mul_v3_v3s1(c.rootDiff, p.keys[s].radius)
                # print(co)
                co[2] = p.roundness * (np.random.rand()*2-1)
                ####
                # if(s<5):
                #     rott = [1.,0,0,0]
                # else:
                #     rott = [0.7071, 0, -0.7071, 0]
                # co = utils.mul_v3_qtv3(rott, co)
                ####
                co = utils.mul_v3_qtv3(p.keys[s].rot, co)
                # print(p.keys[s].co)
                # print(co)
                if (p.keys[s].random != 0.):
                    co = (co[0] + (np.random.rand()*2-1)*p.keys[s].random, co[1] + (np.random.rand()*2-1)*p.keys[s].random, co[2] + (np.random.rand()*2-1)*p.keys[s].random)
                print(p.keys[s].co, co)
                bpy.context.scene.hsysTar.psys.particles[c.num].hair_keys[s].co = p.keys[s].co + mathutils.Vector(co)
        # utils.particleEditNotify()