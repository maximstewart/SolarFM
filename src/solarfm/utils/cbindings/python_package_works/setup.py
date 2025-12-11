# Python imports
from setuptools import setup, Extension
from subprocess import check_output

# Lib imports

# Application imports



pkg_config_args = ["gdk-pixbuf-2.0", "cairo", "gtk"]

def get_pkgconfig_flags(flag_type):
    return check_output(["pkg-config", flag_type] + pkg_config_args).decode().split()

ext = Extension(
    "gtkmemreaper",
    sources              = ["gtkmemreaper.c"],
    include_dirs       = [],
    extra_compile_args = get_pkgconfig_flags("--cflags"),
    extra_link_args    = get_pkgconfig_flags("--libs")
)

setup(
    name = "gtkmemreaper",
    version = "0.1",
    ext_modules = [ext]
)
