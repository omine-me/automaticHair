import bpy, mathutils
import numpy as np
from .utils import *
from . import const
# from datetime import datetime
# from concurrent.futures import ProcessPoolExecutor

class Key:
    def __init__(self, co):
        self.co = mathutils.Vector(co)
        self.radius = .1
        self.rot = [1., 0, 0, 0]
        self.random = 0.
        self.braid = 0.
        self.amp = .05
        self.freq = 5.

class TarHair:
    def __init__(self, ctrlHairNum, tarHairNum, psys):
        self.num = tarHairNum
        # self.rootDiff = psys.particles[tarHairNum].hair_keys[0].co - psys.particles[ctrlHairNum].hair_keys[0].co
        self.rootDiff = const.rootDataPos[tarHairNum] - const.rootDataPos[ctrlHairNum]

class CtrlHair:
    def __init__(self, idx, isCtrl, parAndChilds=None, psys=None, tarHairKeyPos=None):
        self.roundness = 0.
        # self.isCtrl = True if idx == parAndChilds[0] else False
        self.isCtrl = isCtrl
        # self.まとまりのrandomness
        self.ctrlNum = idx
        # self.tarNum = parAndChilds[0]
        # self.childNum = parAndChilds[1:]
        self.tarHair = []
        self.keys = []
        if isCtrl:
            for i in range(psys.settings.hair_step+1):
                self.keys.append(Key(tarHairKeyPos))
            for i in range(len(parAndChilds)):
                self.tarHair.append(TarHair(parAndChilds[0], parAndChilds[i], psys))

class HairCtrlSystem:
    def __init__(self, parent=None, obj=None, isFromData=False):
        if parent is not None:
            self.tarObj = obj
            self.parentNum = set(parent)
            self.parentWeight = {key : 1 for key in parent}
            self.ctrlHair = []
            C = bpy.context
            pLen = len(parent)

            parChildCorr = np.full((pLen, 10), -1) #10 is tmp, so diferrent num is fine
            parChildCorr[:,0] = parent #array's first column is for parent

            C.tool_settings.particle_edit.display_step = 7
            C.tool_settings.particle_edit.use_preserve_length = False

            bpy.ops.object.particle_system_add()
            psys = C.active_object.particle_systems.active
            psys.name = "AutoHairTarget"
            psys.settings.name = "AutoHairTargetParticleSettings"
            psys.settings.type = "HAIR"
            psys.settings.count = const.DEFAULTHAIRNUM
            psys.settings.hair_step = 99#49
            psys.settings.display_step = 5
            targetName = C.active_object.name
            hairCount = psys.settings.count
            psys.settings.hair_length = 0

            bpy.types.Scene.hsysTar = HairTarSystem(C.active_object, psys.name)
            # tarParPos = np.empty((pLen, C.scene.hsysTar.psys.settings.hair_step+1, 3))
            C.scene.hsysTar._particleEditMode()
            C.scene.hsysTar._setDepsgpaph()
            ### set root pos to do properly getClosestParNum()
            # if not isFromData:
            #     for i in range(C.scene.hsysTar.psys.settings.count):
            #         # for j in range(C.scene.hsysTar.psys.settings.hair_step+1):
            #         C.scene.hsysTar.psys.particles[i].hair_keys[0].co = const.rootPos[i]
            # else:
            for i in range(C.scene.hsysTar.psys.settings.count):
                # for j in range(C.scene.hsysTar.psys.settings.hair_step+1):
                C.scene.hsysTar.psys.particles[i].hair_keys[0].co = const.rootDataPos[i]
            # particleEditNotify()
            # C.scene.hsysTar._setDepsgpaph()
            # for idx, i in enumerate(self.parentNum):
            #     for j in range(C.scene.hsysTar.psys.settings.hair_step+1):
            #         tarParPos[idx,j,:] = C.scene.hsysTar.psys.particles[i].hair_keys[j].co
            
            # get child hair of each parent hair
            j = 0
            for i in range(hairCount):
                if not (i in parent):
                    parNumIdx, _ = C.scene.hsysTar._getClosestParNum(i, self.parentNum)
                    if parChildCorr[parNumIdx, -1] != -1:
                        parChildCorr = np.append(parChildCorr, np.full([pLen,1],-1), axis=1)
                    parChildCorr[parNumIdx, parChildCorr[parNumIdx,:].argmin()] = i

                    self.ctrlHair.append(CtrlHair(i, False))
                else:
                    self.ctrlHair.append(CtrlHair(i, True, parChildCorr[j, :], C.scene.hsysTar.psys, const.rootDataPos[i]))
                    j = j+1
            
            # for i in range(pLen):
            # j = 0
            # for i in range(hairCount):
            #     if i in parChildCorr[:,0]:
            #         # self.ctrlHair.append(CtrlHair(i, True, parChildCorr[j, :], C.scene.hsysTar.psys, tarParPos[j, :, :]))
            #         self.ctrlHair.append(CtrlHair(i, True, parChildCorr[j, :], C.scene.hsysTar.psys, const.rootDataPos[i]))
            #         j = j+1
            #     else:
            #         self.ctrlHair.append(CtrlHair(i, False))
            
            particleEditNotify()
            bpy.ops.particle.particle_edit_toggle()

            #active is changed to duplicated obj
            bpy.ops.object.duplicate_move()
            C.active_object.name = targetName + "(AutoHairControler)"
            self.ctrlObj = C.active_object
            bpy.ops.transform.translate(value=(-.4,0,0))
            # bpy.ops.object.particle_system_remove()
            # bpy.ops.object.particle_system_add()
            self.psys = C.active_object.particle_systems.active
            self.psys.name = self.psysName = "AutoHairControl"
            self.psys.settings.name = "AutoHairControlParticleSettings"
            self.psys.settings.type = "HAIR"
            self.psys.settings.count = hairCount
            self.psys.settings.hair_step = 99#9
            self.psys.settings.display_step = 5
            self.psys.settings.emit_from = "FACE"
            # self.psys.settings.hair_length = 0
            
            self._particleEditMode()
            self._setDepsgpaph()
            C.tool_settings.particle_edit.use_preserve_root = True
            ### for i in range(hairCount):
            ###     for j in range(self.psys.settings.hair_step+1):
            ###         self.psys.particles[i].hair_keys[j].co = self.psys.particles[i].hair_keys[0].co
            ## for idx, i in enumerate(self.parentNum):
            ##     # if h.isCtrl:
            ##     for j in range(self.psys.settings.hair_step+1):
            ##         self.psys.particles[i].hair_keys[j].co = tarParPos[idx,j,:]
            # for i in range(self.psys.settings.count):
            #     for j in range(self.psys.settings.hair_step+1):
            #         if i in self.parentNum:
            #             self.psys.particles[i].hair_keys[j].co = [const.rootPos[i][0], const.rootPos[i][1], const.rootPos[i][2]+.05*j]
            #         else:
            #             self.psys.particles[i].hair_keys[j].co = const.rootPos[i]
            particleEditNotify()
            # bpy.ops.particle.particle_edit_toggle()
    
    def updateCtrlHair(self, p):
        # for th in p.tarHair:
        #     # get closest ctrl hair
        C = bpy.context
        C.scene.hsysTar._particleEditMode()
        C.scene.hsysTar._setDepsgpaph()
        if p.isCtrl:
            self.parentNum.add(p.ctrlNum)
            self.parentWeight[p.ctrlNum] = 1
            #すべてをclosestpos ->引っかかったのを remove 後append
            for i in range(C.scene.hsysTar.psys.settings.count):
                if not (i in self.parentNum):
                    _, parNum = C.scene.hsysTar._getClosestParNum(i, self.parentNum)
                    # check whether the tarHair belongs to new ctrl hair 
                    if parNum == p.ctrlNum:
                        # find ctrlHair currently having tarHair 
                        for ctIdx, h in enumerate(C.scene.hsysCtrl.ctrlHair):
                            for tIdx, t in enumerate(h.tarHair):
                                if t.num == i:
                                    delCtIdx = ctIdx
                                    delTIdx = tIdx
                                    # add tarHair to new ctrlHair
                                    # for nh in C.scene.hsysCtrl.ctrlHair:
                                    #     if nh.ctrlNum == parNum:
                                    p.tarHair.append(TarHair(parNum, i, C.scene.hsysTar.psys))
                                    # delete tarHair from current ctrlHair
                                    del(C.scene.hsysCtrl.ctrlHair[delCtIdx].tarHair[delTIdx])
                                    break
                            else:
                                continue
                            break
        else:
            self.parentNum.discard(p.ctrlNum)
            self.parentWeight.pop(p.cutlNum, None)
            for t in p.tarHair:
                parNumIdx, parNum = C.scene.hsysTar._getClosestParNum(t.num, self.parentNum)
                for ctIdx, h in enumerate(C.scene.hsysCtrl.ctrlHair):
                    if h.ctrlNum == parNum:
                        h.tarHair.append(t)
                        h.tarHair[-1].rootDiff\
                                    = C.scene.hsysTar.psys.particles[h.tarHair[-1].num].hair_keys[0].co\
                                    - C.scene.hsysTar.psys.particles[h.ctrlNum].hair_keys[0].co
            p.tarHair = []

    def _particleEditMode(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
            bpy.context.view_layer.objects.active = self.ctrlObj
            bpy.context.object.particle_systems.active_index = 0
        # if bpy.context.object.mode != "PARTICLE_EDIT":
        bpy.ops.particle.particle_edit_toggle()

    def _setDepsgpaph(self):
        # if bpy.context.object.mode == "PARTICLE_EDIT":
        #     bpy.ops.particle.particle_edit_toggle()
        #     bpy.context.view_layer.objects.active = self.ctrlObj
        #     bpy.context.object.particle_systems.active_index = 0
        #     # if bpy.context.object.mode != "PARTICLE_EDIT":
        #     bpy.ops.particle.particle_edit_toggle()
        self.psys = self.ctrlObj.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[self.psysName]

    
    # def setArrayedChild(self):
    #     # for p in self.ctrlHair:
    #     for p in self.parentNum:
    #         # if p.isCtrl:
    #         self._particleEditMode()
    #         self._setDepsgpaph()
    #         prevTan = np.array([0., 0., 0.])
    #         for s in range(self.psys.settings.hair_step+1):
    #             prevTan = self._setKeyRotation(self.ctrlHair[p], s, prevTan)
    #         self.ctrlHair[p].keys[-1].rot = self.ctrlHair[p].keys[-2].rot #set last keys
    #         bpy.context.scene.hsysTar._offsetChild(self.ctrlHair[p])
    #         particleEditNotify()
    #     self._particleEditMode()
    
    def setArrayedChild(self):
        # for p in self.ctrlHair:
        self._particleEditMode()
        self._setDepsgpaph()
        hsysTar = bpy.context.scene.hsysTar
        hs = self.psys.settings.hair_step+1
        for p in self.parentNum:
            if len(self.ctrlHair[p].tarHair) > 1: ### when ctrlHair doesn't have other tarHair, don't caluculate
                prevTan = np.array([0., 0., 0.])
                for s in range(hs):
                    prevTan = self._setKeyRotation(self.ctrlHair[p], s, prevTan)
                self.ctrlHair[p].keys[-1].rot = self.ctrlHair[p].keys[-2].rot #set last keys

        for p in self.parentNum:
            hsysTar._offsetChild(self.ctrlHair[p])
            print(p)
        self._particleEditMode()
    
    def getSelected(self):
        bpy.ops.particle.selected()
        s = {}
        for i in range(self.psys.settings.count):
            for j in range(self.psys.settings.hair_step+1):
                if bpy.context.active_object.particle_systems.active.particles[i].hair_keys[j].is_selected: #use bpy.data
                    s.setdefault(i,[]).append(j)
        return s
    
    def _setKeyRotation(self, p, s, prevTan):
        if s == 0:
            pass
        elif s == 1:
            prevTan = sub_norm_v3_v3v3(self.psys.particles[p.ctrlNum].hair_keys[1].co, self.psys.particles[p.ctrlNum].hair_keys[0].co)
            p.keys[0].rot = [1, 0, 0, 0]
        else:
            tan = sub_norm_v3_v3v3(self.psys.particles[p.ctrlNum].hair_keys[s].co, self.psys.particles[p.ctrlNum].hair_keys[s-1].co)
            cosangle = dot_fl_v3v3(tan, prevTan)
            if (cosangle > 0.999999): #tan and prevTan are opposite
                p.keys[s-1].rot = p.keys[s-2].rot
            else:
                angle = np.arccos(cosangle)
                norm = norm_v3_v3(np.cross(prevTan, tan))
                q = axis_angle_to_quat(norm, angle) #when angle is 1 or -1, q = [1,0,0,0]
                p.keys[s-1].rot = mul_qt_qtqt(q, p.keys[s-2].rot)
            
            prevTan = tan
        return prevTan
    
    def _setKeyPos(self):
        self._setDepsgpaph()
        for i in self.parentNum:
            # if self.ctrlHair[i].isCtrl:
            for j in range(self.psys.settings.hair_step+1):
                self.ctrlHair[i].keys[j].co = mathutils.Vector(self.psys.particles[i].hair_keys[j].co)
    
    def updatePos(self):
        self._setKeyPos()
        # print("end setkeyPos",datetime.now().strftime("%H:%M:%S"))
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
    
    def _particleEditMode(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
            bpy.context.view_layer.objects.active = self.obj
            bpy.context.object.particle_systems.active_index = 0
        # if bpy.context.object.mode != "PARTICLE_EDIT":
        bpy.ops.particle.particle_edit_toggle()

    def _setDepsgpaph(self):
        # if bpy.context.object.mode == "PARTICLE_EDIT":
        #     bpy.ops.particle.particle_edit_toggle()
        #     bpy.context.view_layer.objects.active = self.obj
        #     bpy.context.object.particle_systems.active_index = 0
        #     # if bpy.context.object.mode != "PARTICLE_EDIT":
        #     bpy.ops.particle.particle_edit_toggle()
        self.psys = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[self.psysName]
        # bpy.context.scene.tool_settings.particle_edit.use_preserve_length = False

    def _getClosestParNum(self, child, parents):
        # childPos = bpy.context.scene.hsysTar.psys.particles[child].hair_keys[0].co
        childPos = const.rootDataPos[child]
        
        minDistance = 99999
        shortestParIdx = -1
        for idx, p in enumerate(parents):
            # parPos = bpy.context.scene.hsysTar.psys.particles[p].hair_keys[0].co
            parPos = const.rootDataPos[p]
            distance = abs(childPos[0] - parPos[0]) + abs(childPos[1] - parPos[1]) + abs(childPos[2] - parPos[2])
            
            if distance < minDistance:
                minDistance = distance
                shortestParIdx = idx
                shortestPar = p
        
        return shortestParIdx, shortestPar

    def checkIfInside(self, pos):
        _, cPos, nor, _ = bpy.context.active_object.closest_point_on_mesh(pos)
        if np.dot(nor, cPos-pos)>0:
            return cPos
        return pos

    def _offsetChild(self, p):
        bpy.context.scene.hsysTar._particleEditMode()
        bpy.context.scene.hsysTar._setDepsgpaph()
        psys = bpy.context.scene.hsysTar.psys
        for c in p.tarHair:
            if p.ctrlNum == c.num:
                for k in range(1, psys.settings.hair_step+1):
                    psys.particles[c.num].hair_keys[k].co = p.keys[k].co
            else:
                for k in range(1, psys.settings.hair_step+1):
                    # pass
                    co = mul_v3_v3s1(c.rootDiff, p.keys[k].radius)
                    co[2] = p.roundness * (np.random.rand()*2-1)
                    co = mul_v3_qtv3(p.keys[k].rot, co)
                    if (p.keys[k].braid != 0):
                        co = self._doKink(p, co, k/psys.settings.hair_step+1,k)
                    if (p.keys[k].random != 0.):
                        co = (co[0] + (np.random.rand()*2-1)*p.keys[k].random, co[1] + (np.random.rand()*2-1)*p.keys[k].random, co[2] + (np.random.rand()*2-1)*p.keys[k].random)
                    psys.particles[c.num].hair_keys[k].co = self.checkIfInside(p.keys[k].co + mathutils.Vector(co))
                    # setattr(psys.particles[c.num].hair_keys[k], "co", p.keys[k].co + mathutils.Vector(co))

    # def tmp(self,p):
    #     import time
    #     s = time.perf_counter()
    #     for c in p.tarHair:
    #         for k in range(1, bpy.context.scene.hsysTar.psys.settings.hair_step+1):
    #             co = mul_v3_v3s1(c.rootDiff, p.keys[k].radius)
    #             co[2] = p.roundness * (np.random.rand()*2-1)
    #             co = mul_v3_qtv3(p.keys[k].rot, co)
    #             if (p.keys[k].braid != 0):
    #                 co = self._doKink(p, co, k/bpy.context.scene.hsysTar.psys.settings.hair_step+1,k)
    #             if (p.keys[k].random != 0.):
    #                 co = (co[0] + (np.random.rand()*2-1)*p.keys[k].random, co[1] + (np.random.rand()*2-1)*p.keys[k].random, co[2] + (np.random.rand()*2-1)*p.keys[k].random)
    #             # bpy.context.scene.hsysTar.psys.particles[c.num].hair_keys[k].co = p.keys[k].co + mathutils.Vector(co)
    #             setattr(bpy.context.scene.hsysTar.psys.particles[c.num].hair_keys[k], "co", p.keys[k].co + mathutils.Vector(co))

    #     e = time.perf_counter()
    #     print("test_second:", e - s)
        
    def _doKink(self, p, co, time, k):
        # kink = [1., 0., 0.]
        # q1 = [1., 0., 0., 0.]
        t = time * p.keys[k].freq * np.pi

        #when emit from face
        dt = np.abs(t)
        dt = clamp(dt, 0., np.pi)
        dt = np.sin(dt/2.)

        # result = co
        parVec = sub_v3_v3v3(p.keys[k].co, co)

        # PART_KINK_BRAID
        yVec = mul_v3_qtv3(p.keys[k].rot, [0., 1., 0.])
        zVec = mul_v3_qtv3(p.keys[k].rot, [0., 0., 1.])
        # zVec = mul_v3_qtv3(p.keys[k].rot, [1., 0., 0.])

        parVec = -parVec
        vecOne = norm_v3_v3(parVec)

        inpY = dot_fl_v3v3(yVec, vecOne)
        inpZ = dot_fl_v3v3(zVec, vecOne)

        if(inpY > .5):
            state_co = yVec
            yVec = mul_v3_v3s1(yVec, p.keys[k].amp * np.cos(t))
            zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * np.sin(2. * t))
        elif(inpZ > 0.):
            state_co = mul_v3_v3s1(zVec, np.sin(np.pi / 3.0))
            state_co += mul_v3_v3s1(yVec, -.5)
            yVec = mul_v3_v3s1(yVec, -p.keys[k].amp*np.cos(t + np.pi /3.))
            zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * np.cos(2. * t + np.pi / 6.))
        else:
            state_co = mul_v3_v3s1(zVec, -np.sin(np.pi/3.))
            state_co += mul_v3_v3s1(yVec, -.5)

            yVec = mul_v3_v3s1(yVec, p.keys[k].amp * -np.sin(t + np.pi / 6.))
            zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * -np.sin(2. * t + np.pi / 3.))
        
        state_co = mul_v3_v3s1(state_co, p.keys[k].amp)
        state_co = add_v3_v3v3(state_co, p.keys[k].co)
        parVec = sub_v3_v3v3(co, mathutils.Vector(state_co))

        length = norm_s1_v3(parVec)
        parVec = mul_v3_v3s1(parVec, min(length, p.keys[k].amp / 2.))

        # state_co = add_v3_v3v3(p.keys[k].co, yVec)
        state_co = add_v3_v3v3(mathutils.Vector((0,0,0)), yVec)
        state_co = add_v3_v3v3(state_co, zVec)
        state_co = add_v3_v3v3(state_co, parVec)

        state_co = mul_v3_v3s1(state_co, p.keys[k].braid)

        # END OF PART_KINK_BRAID

        # if (dt < 1.):
        #     co = interp_v3_v3v3(co, result, dt)
        # else:
        #     co = result
        # return co
        return state_co

# def tmp(self,c):
#     import time
#     s = time.perf_counter()
#     # for c in p.tarHair:
#     for k in range(1, bpy.context.scene.hsysTar.psys.settings.hair_step+1):
#         co = mul_v3_v3s1(c.rootDiff, p.keys[k].radius)
#         co[2] = p.roundness * (np.random.rand()*2-1)
#         co = mul_v3_qtv3(p.keys[k].rot, co)
#         if (p.keys[k].braid != 0):
#             pass
#             # co = self._doKink(p, co, k/bpy.context.scene.hsysTar.psys.settings.hair_step+1,k)
#         if (p.keys[k].random != 0.):
#             co = (co[0] + (np.random.rand()*2-1)*p.keys[k].random, co[1] + (np.random.rand()*2-1)*p.keys[k].random, co[2] + (np.random.rand()*2-1)*p.keys[k].random)
#         bpy.context.scene.hsysTar.psys.particles[c.num].hair_keys[k].co = p.keys[k].co + mathutils.Vector(co)