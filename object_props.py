import bpy
from bpy.types import PropertyGroup
from .enums.enums import geometry_types
# A cutter item used by cutters_collection


class MT_Cutter_Item(PropertyGroup):
    def update_use_cutter(self, context):
        if self.parent is not "":
            parent_obj = bpy.data.objects[self.parent]
            bool_mod = parent_obj.modifiers[self.name + '.bool']
            bool_mod.show_viewport = self.value

    name: bpy.props.StringProperty(
        name="Cutter Name")
    value: bpy.props.BoolProperty(
        name="",
        default=True,
        update=update_use_cutter)
    parent: bpy.props.StringProperty(
        name="")


class MT_Preview_Materials(PropertyGroup):
    """Used to store a list of preview materials during baking.

    When we hit the Make3D button maketile assigns the secondary material to the entire
    mesh so we only see actual displacement. We store what materials have been assigned
    to what vertex groups here so we can reassign them to the object later

    Args:
        PropertyGroup (bpy.types.PropertyGroup): Parent class
    """

    vertex_group: bpy.props.StringProperty(
        name="vertex group"
    )

    material: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="material"
    )


class MT_Object_Properties(PropertyGroup):
    is_mt_object: bpy.props.BoolProperty(
        name="Is MakeTile Object",
        default=False
    )

    is_converted: bpy.props.BoolProperty(
        name="Is Converted",
        default=False
    )

    tile_name: bpy.props.StringProperty(
        name="Tile Name"
    )

    geometry_type: bpy.props.EnumProperty(
        name="Geometry Type",
        items=geometry_types
    )

    cutters_collection: bpy.props.CollectionProperty(
        name="Cutters Collection",
        type=MT_Cutter_Item,
        description="Collection of booleans that can be turned on or off by MakeTile."
    )

    disp_mod_name: bpy.props.StringProperty(
        name="Displacement Modifier Name",
        default='MT Displacement'
    )

    subsurf_mod_name: bpy.props.StringProperty(
        name="Subsurf Modifier Name",
        default="MT Subsurf"
    )

    disp_texture: bpy.props.PointerProperty(
        name="Displacement Texture",
        type=bpy.types.ImageTexture
    )

    penstate: bpy.props.BoolProperty(
        name="Pen State",
        description="Used by bmturtle. If penstate is true turtle draws on move",
        default=False
    )

    preview_materials: bpy.props.CollectionProperty(
        name="Preview materials",
        type=MT_Preview_Materials
    )


def register():
    # Property group that contains properties of an object stored on the object
    bpy.types.Object.mt_object_props = bpy.props.PointerProperty(
        type=MT_Object_Properties
    )


def unregister():
    del bpy.types.Object.mt_object_props
