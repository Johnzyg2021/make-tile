import os
import bpy
from bpy.utils import register_class, unregister_class

# File and directory handling
def get_path():
    """returns addon path"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_addon_name():
    """returns file path name of calling file"""
    return os.path.basename(get_path())


def get_prefs():
    """returns MakeTile preferences"""
    return bpy.context.preferences.addons[get_addon_name()].preferences


def register_classes(classlist):
    for cls in classlist:
        register_class(cls)


def unregister_classes(classlist):
    for cls in classlist:
        unregister_class(cls)

def get_default_units():
    prefs = get_prefs()
    return prefs.default_units


def get_default_tile_blueprint():
    prefs = get_prefs()
    return prefs.default_tile_blueprint


def get_default_tile_main_system():
    prefs = get_prefs()
    return prefs.default_tile_main_system


def get_default_base_system():
    prefs = get_prefs()
    return prefs.default_base_system
