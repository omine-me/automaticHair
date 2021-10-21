// #define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>

static PyObject * sample_add(PyObject *self, PyObject *args) {
    int x, y, z;

    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }

    z = x + y;
    return PyLong_FromLong(z);
}

static PyObject * mul_v3_qtv3(PyObject *self, PyObject *args){
    PyObject  *raw_r_list, *raw_q_list;
		// double r[3], q, tmp;
		double r1,r2,r0,q1,q2,q3,q0,tmp;
    //引数
    if(!PyArg_ParseTuple(args, "OO", &raw_q_list, &raw_r_list)){
			// printf("argError");
			return NULL;
		}
		// r1 =  PyFloat_AsDouble(PyList_GetItem(raw_r_list, 0));
		// // printf(raw_r_list);PySequence_List(
		raw_r_list = PySequence_List(raw_r_list);
		r0 =  PyFloat_AsDouble(PyList_GetItem(raw_r_list, 0));
		r1 =  PyFloat_AsDouble(PyList_GetItem(raw_r_list, 1));
		r2 =  PyFloat_AsDouble(PyList_GetItem(raw_r_list, 2));
		q0 =  PyFloat_AsDouble(PyList_GetItem(raw_q_list, 0));
		q1 =  PyFloat_AsDouble(PyList_GetItem(raw_q_list, 1));
		q2 =  PyFloat_AsDouble(PyList_GetItem(raw_q_list, 2));
		q3 =  PyFloat_AsDouble(PyList_GetItem(raw_q_list, 3));
		// q = PyFloat_AsDouble(PyList_GetItem(raw_q_list, 0));

		tmp = -q1 * r0 - q2 * r1 - q3 * r2;
    r2 = q0 * r2 + q1 * r1 - q2 * r0;
    r0 = q0 * r0 + q2 * r2 - q3 * r1;
    r1 = q0 * r1 + q3 * r0 - q1 * r2;

    r2 = tmp * -q3 + r2 * q0 - r0 * q2 + r1 * q1;
    r0 = tmp * -q1 + r0 * q0 - r1 * q3 + r2 * q2;
    r1 = tmp * -q2 + r1 * q0 - r2 * q1 + r0 * q3;
		// *tmp = -q[1] * r[0] - q[2] * r[1] - q[3] * r[2];
    // r[2] = q[0] * r[2] + q[1] * r[1] - q[2] * r[0];
    // r[0] = q[0] * r[0] + q[2] * r[2] - q[3] * r[1];
    // r[1] = q[0] * r[1] + q[3] * r[0] - q[1] * r[2];

    // r[2] = tmp * -q[3] + r[2] * q[0] - r[0] * q[2] + r[1] * q[1];
    // r[0] = tmp * -q[1] + r[0] * q[0] - r[1] * q[3] + r[2] * q[2];
    // r[1] = tmp * -q[2] + r[1] * q[0] - r[2] * q[1] + r[0] * q[3];
		PyList_SetItem(raw_r_list, 0, Py_BuildValue("d", r0));
		PyList_SetItem(raw_r_list, 1, Py_BuildValue("d", r1));
		PyList_SetItem(raw_r_list, 2, Py_BuildValue("d", r2));
		// // printf(raw_r_list);
		return raw_r_list;
}

static PyObject * mul_qt_qtqt(PyObject *self, PyObject *args){
    PyObject  *raw_a_list, *raw_b_list;
		// double r[3], q, tmp;
		// double r1,r2,r0,q1,q2,q3,q0,tmp;
    double a[4], b[4], q[4];
    //引数
    if(!PyArg_ParseTuple(args, "OO", &raw_a_list, &raw_b_list)){
			// printf("argError");
			return NULL;
		}
    raw_a_list = PySequence_List(raw_a_list);
    raw_b_list = PySequence_List(raw_b_list);
		a[0] =  PyFloat_AsDouble(PyList_GetItem(raw_a_list, 0));
		a[1] =  PyFloat_AsDouble(PyList_GetItem(raw_a_list, 1));
		a[2] =  PyFloat_AsDouble(PyList_GetItem(raw_a_list, 2));
		a[3] =  PyFloat_AsDouble(PyList_GetItem(raw_a_list, 3));
		b[0] =  PyFloat_AsDouble(PyList_GetItem(raw_b_list, 0));
		b[1] =  PyFloat_AsDouble(PyList_GetItem(raw_b_list, 1));
		b[2] =  PyFloat_AsDouble(PyList_GetItem(raw_b_list, 2));
		b[3] =  PyFloat_AsDouble(PyList_GetItem(raw_b_list, 3));

		q[3] = a[0] * b[3] + a[3] * b[0] + a[1] * b[2] - a[2] * b[1];
    q[0] = a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3];
    q[1] = a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2];
    q[2] = a[0] * b[2] + a[2] * b[0] + a[3] * b[1] - a[1] * b[3];

		PyList_SetItem(raw_a_list, 0, Py_BuildValue("d", q[0]));
		PyList_SetItem(raw_a_list, 1, Py_BuildValue("d", q[1]));
		PyList_SetItem(raw_a_list, 2, Py_BuildValue("d", q[2]));
		PyList_SetItem(raw_a_list, 3, Py_BuildValue("d", q[3]));
		// // printf(raw_r_list);
		return raw_a_list;
}

static PyObject * axis_angle_to_quat(PyObject *self, PyObject *args){
    PyObject  *raw_norm_list;
    double angle, n[3], phi, si;
    if(!PyArg_ParseTuple(args, "Od", &raw_norm_list, &angle)){
			// printf("argError");
			return NULL;
		}
		phi = 0.5 * angle;
    si = sin(phi);
    raw_norm_list = PySequence_List(raw_norm_list);
    n[0] =  PyFloat_AsDouble(PyList_GetItem(raw_norm_list, 0));
		n[1] =  PyFloat_AsDouble(PyList_GetItem(raw_norm_list, 1));
		n[2] =  PyFloat_AsDouble(PyList_GetItem(raw_norm_list, 2));
    

    PyObject* res = PyList_New(4);
		PyList_SetItem(res, 0, Py_BuildValue("d", cos(phi)));
		PyList_SetItem(res, 1, Py_BuildValue("d", n[0]*si));
		PyList_SetItem(res, 2, Py_BuildValue("d", n[1]*si));
		PyList_SetItem(res, 3, Py_BuildValue("d", n[2]*si));
		// // printf(raw_r_list);
		return res;
}

void acrossb(double *c,double a[],double b[])
{
  // printf("arossb");
  // printf("%lf\n", a[0]);
  c[0]=a[1]*b[2]-a[2]*b[1];
  c[1]=a[2]*b[0]-a[0]*b[2];
  c[2]=a[0]*b[1]-a[1]*b[0];
  // printf("%lf\n", c[0]);
}
void dot_fl_v3v3(double *c, double a[], double b[]){
  *c = a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
  if (*c < -1){
    *c = -1;
  }else if(*c>1){
    *c = 1;
  }
}
void norm_v3_v3(double *a, double b[]){
  double l = sqrt(b[0]*b[0]+b[1]*b[1]+b[2]*b[2]);
  // printf("%lf\n", l);
  a[0] = b[0]/l;
  a[1] = b[1]/l;
  // printf("%lf\n", a[0]);
  a[2] = b[2]/l;
}
void dainyu_double(double *c, double a[]){
  c[0] = a[0];
  c[1] = a[1];
  c[2] = a[2];
  c[3] = a[3];
}
void axis_angle_to_quat_internal(double *q, double n[], double angle){
  double phi = 0.5 * angle;
  double si = sin(phi);
  
  q[0] = cos(phi);
  q[1] = n[0]*si;
  q[2] = n[1]*si;
  q[3] = n[2]*si;
}
void mul_qt_qtqt_internal(double *q, double a[],double b[]){
  q[3] = a[0] * b[3] + a[3] * b[0] + a[1] * b[2] - a[2] * b[1];
  q[0] = a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3];
  q[1] = a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2];
  q[2] = a[0] * b[2] + a[2] * b[0] + a[3] * b[1] - a[1] * b[3];
}

static PyObject * set_key_rotation(PyObject *self, PyObject *args){
    PyObject  *raw_hk,*raw_hk1,*raw_prevTan,*raw_kRot2;
    double hk[3], hk1[3], prevTan[3], kRot2[4], tan[3], cosangle,angle,norm[3],q[4], kRot1[4];
    if(!PyArg_ParseTuple(args, "OOOO", &raw_hk, &raw_hk1, &raw_prevTan, &raw_kRot2)){
			return NULL;
		}
    // raw_norm_list = PySequence_List(raw_norm_list);
    hk[0] =  PyFloat_AsDouble(PyList_GetItem(raw_hk, 0));
		hk[1] =  PyFloat_AsDouble(PyList_GetItem(raw_hk, 1));
		hk[2] =  PyFloat_AsDouble(PyList_GetItem(raw_hk, 2));
    hk1[0] =  PyFloat_AsDouble(PyList_GetItem(raw_hk1, 0));
		hk1[1] =  PyFloat_AsDouble(PyList_GetItem(raw_hk1, 1));
		hk1[2] =  PyFloat_AsDouble(PyList_GetItem(raw_hk1, 2));
    prevTan[0] =  PyFloat_AsDouble(PyList_GetItem(raw_prevTan, 0));
		prevTan[1] =  PyFloat_AsDouble(PyList_GetItem(raw_prevTan, 1));
		prevTan[2] =  PyFloat_AsDouble(PyList_GetItem(raw_prevTan, 2));
    kRot2[0] =  PyFloat_AsDouble(PyList_GetItem(raw_kRot2, 0));
		kRot2[1] =  PyFloat_AsDouble(PyList_GetItem(raw_kRot2, 1));
		kRot2[2] =  PyFloat_AsDouble(PyList_GetItem(raw_kRot2, 2));
		kRot2[3] =  PyFloat_AsDouble(PyList_GetItem(raw_kRot2, 3));
    // for(int i=0;i<4;++i){
    //    printf("%lf\n", kRot2[i]);
    // }
    //sub_norm_v3_v3v3
    double diff[3] = {hk[0]-hk1[0],hk[1]-hk1[1],hk[2]-hk1[2]};
    norm_v3_v3(tan, diff);
    dot_fl_v3v3(&cosangle, tan, prevTan);
    // for(int i=0;i<3;++i){
    //   printf("%lf\n", tan[i]);
    // }
    if (cosangle > 0.999999){
      dainyu_double(kRot1, kRot2);
    }else{
      angle = acos(cosangle);
      double cross[3];
      acrossb(cross, prevTan, tan);
      norm_v3_v3(norm, cross);
      axis_angle_to_quat_internal(q, norm, angle);
      mul_qt_qtqt_internal(kRot1, q, kRot2);
    }
    // for(int i=0;i<4;++i){
    //   // printf("%lf\n", kRot1[i]);
    // }
    // for(int i=0;i<3;++i){
    //   // printf("%lf\n", tan[i]);
    // }
    
    // return Py_BuildValue("OO", )
    PyObject* resrot1 = PyList_New(4);
    PyObject* restan = PyList_New(3);
		PyList_SetItem(resrot1, 0, Py_BuildValue("d", kRot1[0]));
		PyList_SetItem(resrot1, 1, Py_BuildValue("d", kRot1[1]));
		PyList_SetItem(resrot1, 2, Py_BuildValue("d", kRot1[2]));
		PyList_SetItem(resrot1, 3, Py_BuildValue("d", kRot1[3]));
    PyList_SetItem(restan, 0, Py_BuildValue("d", tan[0]));
		PyList_SetItem(restan, 1, Py_BuildValue("d", tan[1]));
		PyList_SetItem(restan, 2, Py_BuildValue("d", tan[2]));
		// // printf(raw_r_list);
		return Py_BuildValue("OO", resrot1, restan);
}








static PyObject *CpyutilsError;

// メソッドの定義
static PyMethodDef CpyutilsMethods[] = {
    {"mul_v3_qtv3",  (PyCFunction)mul_v3_qtv3, METH_VARARGS, "mul_v3_qtv3."},
    {"mul_qt_qtqt",  (PyCFunction)mul_qt_qtqt, METH_VARARGS, "mul_qt_qtqt."},
    {"axis_angle_to_quat",  (PyCFunction)axis_angle_to_quat, METH_VARARGS, "axis_angle_to_quat."},
    {"set_key_rotation",  (PyCFunction)set_key_rotation, METH_VARARGS, "set_key_rotation."},
    {NULL, NULL, 0, NULL}
};

//モジュールの定義
static struct PyModuleDef cpyutilsmodule = {
    PyModuleDef_HEAD_INIT, "cpyutils", NULL,  -1, CpyutilsMethods
};

//メソッドの初期化
PyMODINIT_FUNC PyInit_cpyutils(void) {
    PyObject *m;

    m = PyModule_Create(&cpyutilsmodule);
    if (m == NULL) {
        return NULL;
    }

    CpyutilsError = PyErr_NewException("cpyutils.error", NULL, NULL);
    Py_XINCREF(CpyutilsError);
    if (PyModule_AddObject(m, "error", CpyutilsError) < 0) {
        Py_XDECREF(CpyutilsError);
        Py_CLEAR(CpyutilsError);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}