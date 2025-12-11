#include <Python.h>
#include <gtk.h>
#include <cairo.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <stdlib.h>

// static PyObject* free_pixbuf(PyObject* self, PyObject* args) {
static void free_pixbuf(PyObject* self, PyObject* args) {
    PyObject *py_pixbuf;

    if (!PyArg_ParseTuple(args, "O", &py_pixbuf)) {
        return NULL;
    }

    GdkPixbuf *pixbuf = (GdkPixbuf *) PyLong_AsVoidPtr(py_pixbuf);
    if (!GDK_IS_PIXBUF(pixbuf)) {
        PyErr_SetString(PyExc_TypeError, "Invalid GdkPixbuf pointer.");
        return NULL;
    }

    g_free(pixbuf);
    // return PyBytes_FromStringAndSize((const char *) cairo_data, buffer_size);
}


static void free_list_store(PyObject* self, PyObject* args) {
    PyObject *py_list_store;

    if (!PyArg_ParseTuple(args, "O", &py_list_store)) {
        return NULL;
    }

    GtkListStore *list_store = (GtkListStore *) PyLong_AsVoidPtr(py_list_store);
    if (!GTK_IS_LIST_STORE(list_store)) {
        PyErr_SetString(PyExc_TypeError, "Invalid Gtk.ListStore pointer.");
        return NULL;
    }

    g_object_unref(list_store);
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
