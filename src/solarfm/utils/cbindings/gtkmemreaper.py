# Python imports
import pkg_resources
import importlib.util

# Lib imports

# Application imports



def __bootstrap__():
    __file__   = pkg_resources.resource_filename(__name__, 'gtkmemreaper.cpython-313-x86_64-linux-gnu.so')
    spec       = importlib.util.spec_from_file_location(
        __name__,
        __file__
    )
    mod        = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

__bootstrap__()
