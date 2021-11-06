import bpy, mathutils
import numpy as np
from .utils import *
from . import const, cpyutils
import datetime
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
        self.rootDiff = list(const.rootDataPos[tarHairNum] - const.rootDataPos[ctrlHairNum])

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
            self.notParentNum = {i for i in range(bpy.context.scene.defaultHairNum)} - self.parentNum
            self.parentWeight = {key : 1 for key in parent}
            self.ctrlHair = []
            C = bpy.context
            pLen = len(parent)

            parChildCorr = np.full((pLen, 1), -1) #10 is tmp, so diferrent num is fine
            parChildCorr[:,0] = parent #array's first column is for parent

            C.tool_settings.particle_edit.display_step = 7
            C.tool_settings.particle_edit.use_preserve_length = False

            bpy.ops.object.particle_system_add()
            psys = C.active_object.particle_systems.active
            psys.name = "AutoHairTarget"
            psys.settings.name = "AutoHairTargetParticleSettings"
            psys.settings.type = "HAIR"
            psys.settings.count = bpy.context.scene.defaultHairNum
            psys.settings.hair_step = 99#49
            psys.settings.display_step = 6
            targetName = C.active_object.name
            hairCount = psys.settings.count
            psys.settings.hair_length = 0

            bpy.types.Scene.hsysTar = HairTarSystem(C.active_object, psys.name, psys.settings.hair_step)
            # tarParPos = np.empty((pLen, C.scene.hsysTar.psys.settings.hair_step+1, 3))
            C.scene.hsysTar._particleEditMode()
            C.scene.hsysTar._setDepsgpaph()
            print("end tarhairInit",datetime.datetime.now())
            ### set root pos to do properly getClosestParNum()
            # if not isFromData:
            #     for i in range(C.scene.hsysTar.psys.settings.count):
            #         # for j in range(C.scene.hsysTar.psys.settings.hair_step+1):
            #         C.scene.hsysTar.psys.particles[i].hair_keys[0].co = const.rootPos[i]
            # else:
            for i in range(C.scene.hsysTar.psys.settings.count):
                C.scene.hsysTar.psys.particles[i].hair_keys[0].co = const.rootDataPos[i]
            print("end tar root set",datetime.datetime.now())
            # get child hair of each parent hair
            j = 0
            for i in range(hairCount):
                if i in self.notParentNum:
                    parNumIdx, _ = C.scene.hsysTar._getClosestParNum(i, self.parentNum)
                    # parNumIdx = 1
                    if parChildCorr[parNumIdx, -1] != -1:
                        parChildCorr = np.append(parChildCorr, np.full([pLen,1],-1), axis=1)
                    parChildCorr[parNumIdx, parChildCorr[parNumIdx,:].argmin()] = i

                    self.ctrlHair.append(CtrlHair(i, False))
                else:
                    self.ctrlHair.append(CtrlHair(i, True, parChildCorr[j, :], C.scene.hsysTar.psys, const.rootDataPos[i]))
                    j = j+1
            print("end getclosest",datetime.datetime.now())
            
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
            self.hairStep = self.psys.settings.hair_step+1
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
            # self.parentWeight[p.ctrlNum] = 1
            #すべてをclosestpos ->引っかかったのを remove 後append
            for i in range(C.scene.hsysTar.psys.settings.count):
                if i in self.notParentNum:
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
            # self.parentWeight.pop(p.cutlNum, None)
            for t in p.tarHair:
                parNumIdx, parNum = C.scene.hsysTar._getClosestParNum(t.num, self.parentNum)
                for ctIdx, h in enumerate(C.scene.hsysCtrl.ctrlHair):
                    if h.ctrlNum == parNum:
                        h.tarHair.append(t)
                        h.tarHair[-1].rootDiff\
                                    = list(C.scene.hsysTar.psys.particles[h.tarHair[-1].num].hair_keys[0].co\
                                    - C.scene.hsysTar.psys.particles[h.ctrlNum].hair_keys[0].co)
            p.tarHair = []

    def _particleEditMode(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
            bpy.context.view_layer.objects.active = self.ctrlObj
            bpy.context.object.particle_systems.active_index = 0
        # if bpy.context.object.mode != "PARTICLE_EDIT":
        bpy.ops.particle.particle_edit_toggle()

    def _setDepsgpaph(self):
        self.psys = self.ctrlObj.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[self.psysName]
    
    def setArrayedChild(self, selected=None):
        # for p in self.ctrlHair:
        self._particleEditMode()
        self._setDepsgpaph()
        # for p in self.parentNum:
        for p in (self.parentNum if selected==None else selected):
            if len(self.ctrlHair[p].tarHair) > 1: ### when ctrlHair doesn't have other tarHair, don't caluculate
                ch = self.ctrlHair[p]
                ps = self.psys.particles[p]
                #process of s == 1
                prevTan = list(sub_norm_v3_v3v3(ps.hair_keys[1].co, ps.hair_keys[0].co))
                ch.keys[0].rot = [1, 0, 0, 0]
                for s in range(2,self.hairStep):
                    # ch.keys[s-1].rot, prevTan = cpyutils.set_key_rotation(list(ps.hair_keys[s].co), list(ps.hair_keys[s-1].co), prevTan, ch.keys[s-2].rot)
                    ch.keys[s-1].rot, prevTan = cpyutils.set_key_rotation(list(ps.hair_keys[s].co), list(ps.hair_keys[s-1].co), list(prevTan), list(ch.keys[s-2].rot))
                ch.keys[-1].rot = ch.keys[-2].rot #set last keys
                # for i in ch.keys:
                #     print(i.rot)
                # print("--------")
        print("end setKeyRot in arrayedChild",datetime.datetime.now())
        hsysTar = bpy.context.scene.hsysTar
        hsysTar._particleEditMode()
        hsysTar._setDepsgpaph()
        # for p in self.parentNum:
        for p in (self.parentNum if selected==None else selected):
            hsysTar._offsetChild(self.ctrlHair[p])
        particleEditNotify()
        self._particleEditMode()
    
    def getSelected(self):
        bpy.ops.particle.selected()
        s = {}
        psys = bpy.context.active_object.particle_systems.active
        for i in range(self.psys.settings.count):
            for j in range(self.hairStep):
                if psys.particles[i].hair_keys[j].is_selected: #use bpy.data
                    s.setdefault(i,[]).append(j)
        return s
    
    # def _setKeyRotation(self, p, s, prevTan, parti):
    #     p.keys[s-1].rot, prevTan = cpyutils.set_key_rotation(list(parti.hair_keys[s].co), list(parti.hair_keys[s-1].co), list(prevTan), p.keys[s-2].rot)
    
    def _setKeyPos(self, selected=None):
        # self._particleEditMode()
        self._setDepsgpaph()
        for i in (self.parentNum if selected==None else selected):
            # if self.ctrlHair[i].isCtrl:
            for j in range(self.hairStep):
                # self.ctrlHair[i].keys[j].co = self.psys.particles[i].hair_keys[j].co
                ### do not enter directly because it is shallow copy
                self.ctrlHair[i].keys[j].co = mathutils.Vector(self.psys.particles[i].hair_keys[j].co)
        particleEditNotify()
    
    def updatePos(self, selected=None):
        self._setKeyPos(selected)
        print("end _setKeyPos",datetime.datetime.now())
        # print("end setkeyPos",datetime.now().strftime("%H:%M:%S"))
        # print(self.ctrlHair[0].keys[1].co)
        self.setArrayedChild(selected)

class HairTarSystem:
    def __init__(self, obj, psysName, step):
        self.obj = obj
        self.psysName = psysName
        self.psys = obj.particle_systems.active
        self.hairStep = step + 1
    
    def _particleEditMode(self):
        if bpy.context.object.mode == "PARTICLE_EDIT":
            bpy.ops.particle.particle_edit_toggle()
            bpy.context.view_layer.objects.active = self.obj
            bpy.context.object.particle_systems.active_index = 0
        bpy.ops.particle.particle_edit_toggle()

    def _setDepsgpaph(self):
        self.psys = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems[self.psysName]

    def _getClosestParNum(self, child, parents):
        # childPos = bpy.context.scene.hsysTar.psys.particles[child].hair_keys[0].co
        childPos = const.rootDataPos[child]
        
        minDistance = 99999
        shortestParIdx = shortestPar = -1
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
        psys = bpy.context.scene.hsysTar.psys
        # print(p.ctrlNum, end='')
        for c in p.tarHair:
            parti = psys.particles[c.num]
            # if p.ctrlNum == c.num: ### this was for reduction of calc cost, but it's not good when braid is not zero.
            #     for k in range(1, self.hairStep):
            #         # pass
            #         parti.hair_keys[k].co = mathutils.Vector(p.keys[k].co)
            #         # parti.hair_keys[k].co = p.keys[k].co
            # else:
            for k in range(1, self.hairStep):
                parti.hair_keys[k].co = mathutils.Vector(cpyutils.offset_child(list(c.rootDiff), \
                                                                                p.keys[k].radius, \
                                                                                list(p.keys[k].rot),\
                                                                                list(p.keys[k].co),\
                                                                                p.roundness,\
                                                                                k,\
                                                                                self.hairStep,\
                                                                                p.keys[k].random,\
                                                                                p.keys[k].braid,\
                                                                                p.keys[k].amp,\
                                                                                p.keys[k].freq))
                # print(p.keys[k].co - parti.hair_keys[k].co)
        
### inplemented in cpyutils
    # def _doKink(self, p, co, time, k):
    #     # kink = [1., 0., 0.]
    #     # q1 = [1., 0., 0., 0.]
    #     t = time * p.keys[k].freq * np.pi

    #     #when emit from face
    #     dt = np.abs(t)
    #     dt = clamp(dt, 0., np.pi)
    #     dt = np.sin(dt/2.)

    #     # result = co
    #     parVec = sub_v3_v3v3(p.keys[k].co, co)

    #     # PART_KINK_BRAID
    #     yVec = mul_v3_qtv3(p.keys[k].rot, [0., 1., 0.])
    #     zVec = mul_v3_qtv3(p.keys[k].rot, [0., 0., 1.])
    #     # zVec = mul_v3_qtv3(p.keys[k].rot, [1., 0., 0.])

    #     parVec = -parVec
    #     vecOne = norm_v3_v3(parVec)

    #     inpY = dot_fl_v3v3(yVec, vecOne)
    #     inpZ = dot_fl_v3v3(zVec, vecOne)

    #     if(inpY > .5):
    #         state_co = yVec
    #         yVec = mul_v3_v3s1(yVec, p.keys[k].amp * np.cos(t))
    #         zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * np.sin(2. * t))
    #     elif(inpZ > 0.):
    #         state_co = mul_v3_v3s1(zVec, np.sin(np.pi / 3.0))
    #         state_co += mul_v3_v3s1(yVec, -.5)
    #         yVec = mul_v3_v3s1(yVec, -p.keys[k].amp*np.cos(t + np.pi /3.))
    #         zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * np.cos(2. * t + np.pi / 6.))
    #     else:
    #         state_co = mul_v3_v3s1(zVec, -np.sin(np.pi/3.))
    #         state_co += mul_v3_v3s1(yVec, -.5)

    #         yVec = mul_v3_v3s1(yVec, p.keys[k].amp * -np.sin(t + np.pi / 6.))
    #         zVec = mul_v3_v3s1(zVec, p.keys[k].amp / 2. * -np.sin(2. * t + np.pi / 3.))
        
    #     state_co = mul_v3_v3s1(state_co, p.keys[k].amp)
    #     state_co = add_v3_v3v3(state_co, p.keys[k].co)
    #     parVec = sub_v3_v3v3(co, mathutils.Vector(state_co))

    #     length = norm_s1_v3(parVec)
    #     parVec = mul_v3_v3s1(parVec, min(length, p.keys[k].amp / 2.))

    #     # state_co = add_v3_v3v3(p.keys[k].co, yVec)
    #     state_co = add_v3_v3v3(mathutils.Vector((0,0,0)), yVec)
    #     state_co = add_v3_v3v3(state_co, zVec)
    #     state_co = add_v3_v3v3(state_co, parVec)

    #     state_co = mul_v3_v3s1(state_co, p.keys[k].braid)

    #     # END OF PART_KINK_BRAID

    #     # if (dt < 1.):
    #     #     co = interp_v3_v3v3(co, result, dt)
    #     # else:
    #     #     co = result
    #     # return co
    #     return state_co