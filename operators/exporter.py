import os
from random import random
import bpy
from .. lib.utils.selection import select, activate, deselect_all
from .. utils.registration import get_prefs
from .. lib.utils.collections import create_collection, add_object_to_collection
from .. enums.enums import units
from .voxeliser import voxelise_and_triangulate


class MT_OT_Export_Tile_Variants(bpy.types.Operator):
    bl_idname = "scene.mt_export_multiple_tile_variants"
    bl_label = "Export multiple tile variants"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        deselect_all()

        objects = bpy.data.objects
        obj = context.active_object
        obj_props = obj.mt_object_props

        # set up exporter options
        blend_units = bpy.context.scene.mt_units
        export_path = context.scene.mt_export_path

        if blend_units == 'CM':
            unit_multiplier = 10
        else:
            unit_multiplier = 25.4

        if not os.path.exists(export_path):
            os.mkdir(export_path)

        # check if active object is a MT object, if so we export everything
        # in the collection corresponding to the object's mt_object_props.tile_name
        if obj_props.is_mt_object is True:
            tile_name = obj_props.tile_name
            tile_collection = bpy.data.collections[tile_name]

            # save list of preview obs to use these for generating variants
            preview_obs = []
            for obj in tile_collection.all_objects:
                if obj.type == 'MESH':
                    if obj.mt_object_props.geometry_type == 'PREVIEW':
                        preview_obs.append(obj)

            # create variants
            i = 0
            while i < context.scene.mt_num_variants:
                for preview_obj in preview_obs:
                    preview_obj.hide_viewport = False
                    select(preview_obj.name)
                    activate(preview_obj.name)

                    for item in preview_obj.material_slots.items():
                        material = bpy.data.materials[item[0]]
                        tree = material.node_tree
                        if 'Seed' in tree.nodes:
                            seed_node = tree.nodes['Seed']
                            rand_seed = random()
                            seed_node.outputs[0].default_value = rand_seed * 1000
                            # bake the displacement map
                            bpy.ops.scene.mt_bake_displacement()

                # save list of visible objects in tile collection
                deselect_all()
                obs = []
                for obj in tile_collection.all_objects:
                    if obj.type == 'MESH':
                        if obj.hide_viewport is False and obj.hide_get() is False:
                            obs.append(obj)
                            select(obj.name)
                            activate(obj.name)

                # Apply all modifiers and create a copy of our meshes
                bpy.ops.object.convert(target='MESH', keep_original=True)

                # hide the original objects
                for obj in obs:
                    obj.hide_set(True)

                # save a list of the copies
                copies = []
                for obj in tile_collection.all_objects:
                    if obj.type == 'MESH':
                        if obj.hide_viewport is False and obj.hide_get() is False:
                            copies.append(obj)

                # join the copies together into one object
                deselect_all()
                for copy in copies:
                    select(copy.name)

                bpy.ops.object.join()

                merged_obj = context.active_object

                # voxelise if necessary
                if context.scene.mt_voxelise_on_export is True:
                    merged_obj = voxelise_and_triangulate(merged_obj)

                # construct filepath
                file_path = os.path.join(context.scene.mt_export_path, merged_obj.name + '.' + str(rand_seed) + '.stl')

                # export our merged object
                bpy.ops.export_mesh.stl(
                    filepath=file_path,
                    check_existing=True,
                    filter_glob="*.stl",
                    use_selection=True,
                    global_scale=unit_multiplier,
                    use_mesh_modifiers=True)


                # Delete merged obj
                objects.remove(objects[obj.name], do_unlink=True)

                # unhide original obj
                for obj in obs:
                    obj.hide_set(False)

                i += 1

        return {'FINISHED'}


class MT_OT_Export_Tile(bpy.types.Operator):
    '''Exports contents of current collection as an .stl.'''

    bl_idname = "scene.mt_export_tile"
    bl_label = "Export tile"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            return bpy.context.object.mode == 'OBJECT'
        else:
            return True

    def execute(self, context):
        objects = bpy.data.objects

        if context.scene.mt_num_variants > 1:
            bpy.ops.scene.mt_export_multiple_tile_variants()
            return {'PASS_THROUGH'}

        deselect_all()

        obj = context.active_object
        obj_props = obj.mt_object_props

        # set up exporter options
        units = bpy.context.scene.mt_units
        export_path = context.scene.mt_export_path

        if units == 'CM':
            unit_multiplier = 10
        else:
            unit_multiplier = 25.4

        if not os.path.exists(export_path):
            os.mkdir(export_path)

        # check if active object is a MT object, if so we export everything
        # in the collection corresponding to the object's mt_object_props.tile_name
        if obj_props.is_mt_object is True:
            tile_name = obj_props.tile_name
            tile_collection = bpy.data.collections[tile_name]

            # save list of visible objects in tile collection
            obs = []
            for obj in tile_collection.all_objects:
                if obj.type == 'MESH':
                    if obj.hide_viewport is False and obj.hide_get() is False:
                        obs.append(obj)
                        obj.select_set(True)

            # cannot get this to work with context override whatever
            # I do so using select

            ctx = {
                'selected_objects': obs,
                'active_object': obs[0],
                'object': obs[0]
            }

            bpy.ops.object.convert(ctx, target='MESH', keep_original=True)


            # hide the original objects
            for obj in obs:
                obj.hide_set(True)

            # save a list of the copies
            copies = []
            for obj in tile_collection.all_objects:
                if obj.type == 'MESH':
                    if obj.hide_viewport is False and obj.hide_get() is False:
                        copies.append(obj)

            # join the copies together into one object
            deselect_all()
            for copy in copies:
                select(copy.name)

            bpy.ops.object.join()

            merged_obj = context.active_object

            # voxelise if necessary
            if context.scene.mt_voxelise_on_export is True:
                merged_obj = voxelise_and_triangulate(merged_obj)

            file_path = os.path.join(context.scene.mt_export_path, merged_obj.name + '.' + str(random()) + '.stl')

            # export our merged object
            bpy.ops.export_mesh.stl(
                filepath=file_path,
                check_existing=True,
                filter_glob="*.stl",
                use_selection=True,
                global_scale=unit_multiplier,
                use_mesh_modifiers=True)

            objects.remove(objects[merged_obj.name], do_unlink=True)
            for obj in obs:
                obj.hide_set(False)

        else:
            obj = context.active_object
            obj_copy = obj.copy()
            obj_copy.data = obj_copy.data.copy()

            if context.scene.mt_voxelise_on_export is True:
                voxelise_and_triangulate(obj_copy)

            select(obj_copy.name)
            file_path = os.path.join(context.scene.mt_export_path, merged_obj.name + '.' + str(random()) + '.stl')

            # export our merged object
            bpy.ops.export_mesh.stl(
                filepath=file_path,
                check_existing=True,
                filter_glob="*.stl",
                use_selection=True,
                global_scale=unit_multiplier,
                use_mesh_modifiers=True)

            # delete copy
            objects.remove(objects[obj_copy.name], do_unlink=True)

        return {'FINISHED'}

    @classmethod
    def register(cls):

        preferences = get_prefs()

        bpy.types.Scene.mt_export_path = bpy.props.StringProperty(
            name="Export Path",
            description="Path to export tiles to",
            subtype="DIR_PATH",
            default=preferences.default_export_path,
        )

        bpy.types.Scene.mt_units = bpy.props.EnumProperty(
            name="Units",
            items=units,
            description="Export units",
            default=preferences.default_units
        )

        bpy.types.Scene.mt_voxelise_on_export = bpy.props.BoolProperty(
            name="Voxelise",
            default=False
        )

        bpy.types.Scene.mt_trim_on_export = bpy.props.BoolProperty(
            name="Trim",
            description="Uses the Trim Tile settings",
            default=False
        )

        bpy.types.Scene.mt_num_variants = bpy.props.IntProperty(
            name="Variants",
            description="Number of variants of tile to export",
            default=1
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.mt_trim_on_export
        del bpy.types.Scene.mt_voxelise_on_export
        del bpy.types.Scene.mt_units
        del bpy.types.Scene.mt_export_path
