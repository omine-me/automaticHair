import numpy as np
import mathutils

def sub_norm_v3_v3v3(key1, key2):
    rawVec = key1 - key2
    return rawVec / np.linalg.norm(rawVec)

def mul_v3_v3s1(a, b):#s1 means scalar
    return mathutils.Vector((a[0] * b, a[1] * b, a[2] * b))

def mul_qt_qtqt(a, b):
    t0 = t1 = t2 = 0.0
    q = np.zeros(4)

    t0 = a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3]
    t1 = a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2]
    t2 = a[0] * b[2] + a[2] * b[0] + a[3] * b[1] - a[1] * b[3]
    q[3] = a[0] * b[3] + a[3] * b[0] + a[1] * b[2] - a[2] * b[1]
    q[0] = t0
    q[1] = t1
    q[2] = t2
    return q

def mul_v3_qtv3(q, r):
    t0 = -q[1] * r[0] - q[2] * r[1] - q[3] * r[2]
    t1 = q[0] * r[0] + q[2] * r[2] - q[3] * r[1]
    t2 = q[0] * r[1] + q[3] * r[0] - q[1] * r[2]
    r[2] = q[0] * r[2] + q[1] * r[1] - q[2] * r[0]
    r[0] = t1
    r[1] = t2

    t1 = t0 * -q[1] + r[0] * q[0] - r[1] * q[3] + r[2] * q[2]
    t2 = t0 * -q[2] + r[1] * q[0] - r[2] * q[1] + r[0] * q[3]
    r[2] = t0 * -q[3] + r[2] * q[0] - r[0] * q[2] + r[1] * q[1]
    r[0] = t1
    r[1] = t2
    return r

def norm_v3_v3(v):
    return v / np.linalg.norm(v)

def axis_angle_to_quat(norm, angle):
    phi = 0.5 * angle
    si = np.sin(phi)
    co = np.cos(phi)
    # return 1
    return [co, norm[0]*si, norm[1]*si, norm[2]*si]