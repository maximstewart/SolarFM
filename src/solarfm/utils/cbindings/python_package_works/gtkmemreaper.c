#include <Python.h>
#include <gtk/gtk.h>
#include <cairo.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <stdlib.h>

// static PyObject* free_pixbuf(PyObject* self, PyObject* args) {
static PyObject* free_pixbuf(PyObject* self, PyObject* args) {
    PyObject *py_pixbuf;

    if (!PyArg_ParseTuple(args, "O", &py_pixbuf)) {
        Py_RETURN_NONE;
    }

    GdkPixbuf *pixbuf = (GdkPixbuf *) PyLong_AsVoidPtr(py_pixbuf);
    if (!GDK_IS_PIXBUF(pixbuf)) {
        PyErr_SetString(PyExc_TypeError, "Invalid GdkPixbuf pointer.");
        Py_RETURN_NONE;
    }

    g_object_unref(pixbuf);
    g_assert_null(pixbuf);
    Py_RETURN_NONE;
}


static PyObject* free_list_store(PyObject* self, PyObject* args) {
    PyObject *py_list_store;

    if (!PyArg_ParseTuple(args, "O", &py_list_store)) {
        Py_RETURN_NONE;
    }

    GtkListStore *list_store = (GtkListStore *) PyLong_AsVoidPtr(py_list_store);
    if (!GTK_IS_LIST_STORE(list_store)) {
        PyErr_SetString(PyExc_TypeError, "Invalid Gtk.ListStore pointer.");
        Py_RETURN_NONE;
    }

    g_object_unref(list_store);
    g_assert_null(list_store);
    Py_RETURN_NONE;
}


static PyMethodDef Methods[] = {
    {"free_pixbuf", free_pixbuf, METH_VARARGS, "Clear GdkPixbuf* ."},
    {"free_list_store", free_list_store, METH_VARARGS, "Clear GtkListStore* ."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "gtkmemreaper",
    NULL,
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_gtkmemreaper(void) {
    return PyModule_Create(&moduledef);
}
