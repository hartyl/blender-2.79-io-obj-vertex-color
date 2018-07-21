# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "3D-Coat Applink",
    "author": "Kalle-Samuli Riihikoski (haikalle)",
    "version": (3, 5, 22),
    "blender": (2, 80, 0),
    "location": "Scene > 3D-Coat Applink",
    "description": "Transfer data between 3D-Coat/Blender",
    "warning": "",
    "wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/3dcoat_applink",
    "category": "Import-Export",
}


if "bpy" in locals():
    import importlib
    importlib.reload(coat)
    importlib.reload(tex)
else:
    from . import tex

from io_coat3D import tex
import os
import ntpath
import re

import time
import bpy
from bpy.types import PropertyGroup
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatVectorProperty,
        StringProperty,
        PointerProperty,
        )


bpy.coat3D = dict()
bpy.coat3D['active_coat'] = ''
bpy.coat3D['status'] = 0
def set_exchange_folder():
    platform = os.sys.platform
    coat3D = bpy.context.scene.coat3D
    Blender_export = ""

    if(platform == 'win32'):
        exchange = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3D-CoatV4' + os.sep +'Exchange'
        if not(os.path.isdir(exchange)):
            exchange = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3D-CoatV3' + os.sep +'Exchange'
    else:
        exchange = os.path.expanduser("~") + os.sep + '3D-CoatV4' + os.sep + 'Exchange'
        if not(os.path.isdir(exchange)):
            exchange = os.path.expanduser("~") + os.sep + '3D-CoatV3' + os.sep + 'Exchange'
    if(not(os.path.isdir(exchange))):
        exchange = coat3D.exchangedir

    if(os.path.isdir(exchange)):
        bpy.coat3D['status'] = 1
        if(platform == 'win32'):
            exchange_path = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender' + os.sep + 'Exchange_folder.txt'
            applink_folder = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender'
            if(not(os.path.isdir(applink_folder))):
                os.makedirs(applink_folder)
        else:
            exchange_path = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender' + os.sep + 'Exchange_folder.txt'
            applink_folder = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender'
            if(not(os.path.isdir(applink_folder))):
                os.makedirs(applink_folder)
        file = open(exchange_path, "w")
        file.write("%s"%(coat3D.exchangedir))
        file.close()

    else:
        if(platform == 'win32'):
            exchange_path = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender' + os.sep + 'Exchange_folder.txt'
        else:
            exchange_path = os.path.expanduser("~") + os.sep + '3DC2Blender' + os.sep + 'Exchange_folder.txt'
        if(os.path.isfile(exchange_path)):
            ex_path =''

            ex_pathh = open(exchange_path)
            for line in ex_pathh:
                ex_path = line
                break
            ex_pathh.close()

            if(os.path.isdir(ex_path) and ex_path.rfind('Exchange') >= 0):
                exchange = ex_path
                bpy.coat3D['status'] = 1
            else:
                bpy.coat3D['status'] = 0
        else:
            bpy.coat3D['status'] = 0
    if(bpy.coat3D['status'] == 1):
        Blender_folder = ("%s%sBlender"%(exchange,os.sep))
        Blender_export = Blender_folder
        path3b_now = exchange
        path3b_now += ('last_saved_3b_file.txt')
        Blender_export += ('%sexport.txt'%(os.sep))

        if(not(os.path.isdir(Blender_folder))):
            os.makedirs(Blender_folder)
            Blender_folder = os.path.join(Blender_folder,"run.txt")
            file = open(Blender_folder, "w")
            file.close()
    return exchange

def set_working_folders():
    platform = os.sys.platform
    coat3D = bpy.context.scene.coat3D
    if(platform == 'win32'):
        if(bpy.data.filepath == ''):
            folder_objects = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender' + os.sep + 'Objects'
            folder_textures = os.path.expanduser("~") + os.sep + 'Documents' + os.sep + '3DC2Blender' + os.sep + 'Textures' + os.sep
        else:
            folder_objects  = os.path.dirname(bpy.data.filepath) + os.sep + '3DCApplink' + os.sep + 'Objects'
            folder_textures = os.path.dirname(bpy.data.filepath) + os.sep + '3DCApplink' + os.sep + 'Textures' + os.sep
        if(not(os.path.isdir(folder_objects))):
            os.makedirs(folder_objects)
        if(not(os.path.isdir(folder_textures))):
            os.makedirs(folder_textures)
    else:
        folder_objects = os.path.expanduser("~") + os.sep + '3DC2Blender' + os.sep + 'Objects'
        folder_textures = os.path.expanduser("~") + os.sep + '3DC2Blender' + os.sep + 'Textures' + os.sep
        if(not(os.path.isdir(folder_objects))):
            os.makedirs(folder_objects)
        if(not(os.path.isdir(folder_textures))):
            os.makedirs(folder_textures)


    return folder_objects,folder_textures

class ObjectButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

class SCENE_PT_Main(ObjectButtonsPanel,bpy.types.Panel):
    bl_label = "3D-Coat Applink"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        me = context.scene.objects
        mat_list = []
        import_no = 0
        coat = bpy.coat3D
        coat3D = bpy.context.scene.coat3D
        if(bpy.context.active_object):
            coa = bpy.context.active_object.coat3D

        if(bpy.coat3D['status'] == 0 and not(os.path.isdir(coat3D.exchangedir))):
            bpy.coat3D['active_coat'] = set_exchange_folder()
            row = layout.row()
            row.label(text="Applink didn't find your 3d-Coat/Excahnge folder.")
            row = layout.row()
            row.label("Please select it before using Applink.")
            row = layout.row()
            row.prop(coat3D,"exchangedir",text="")

        else:
            #Here you add your GUI
            row = layout.row()
            row.prop(coat3D,"type",text = "")
            row = layout.row()
            colL = row.column()
            colR = row.column()

            colR.operator("export_applink.pilgway_3d_coat", text="Transfer")
            colL.operator("import_applink.pilgway_3d_coat", text="Update")



class SCENE_OT_export(bpy.types.Operator):
    bl_idname = "export_applink.pilgway_3d_coat"
    bl_label = "Export your custom property"
    bl_description = "Export your custom property"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        checkname = ''
        coat3D = bpy.context.scene.coat3D
        scene = context.scene
        activeobj = bpy.context.active_object.name
        coa = bpy.context.active_object.coat3D
        coat3D.exchangedir = set_exchange_folder()
        export_ok = False

        folder_objects,folder_textures = set_working_folders()

        if(coat3D.exchange_found == False):
            return {'FINISHED'}

        if(bpy.context.selected_objects == []):
            return {'FINISHED'}
        else:
            for objec in bpy.context.selected_objects:
                if objec.type == 'MESH':
                    export_ok = True
            if(export_ok == False):
                return {'FINISHED'}

        importfile = coat3D.exchangedir
        texturefile = coat3D.exchangedir
        importfile += ('%simport.txt'%(os.sep))
        texturefile += ('%stextures.txt'%(os.sep))

        looking = True
        object_index = 0
        if(coa.applink_address and os.path.isfile(coa.applink_address)):
            checkname = coa.applink_address

        else:
            while(looking == True):
                checkname = folder_objects + os.sep + activeobj
                checkname = ("%s%.2d.dae"%(checkname,object_index))
                if(os.path.isfile(checkname)):
                    object_index += 1
                else:
                    looking = False
                    coa.applink_name = ("%s%.2d"%(activeobj,object_index))
                    coa.applink_address = checkname
        for objekti in bpy.context.selected_objects:
            if(objekti.material_slots.keys() == []):
                bpy.ops.material.new()
                objekti.data.materials.append(bpy.data.materials[-1])

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        #bpy.ops.object.transforms_to_deltas(mode='ROT')

        bpy.ops.wm.collada_export(filepath=coa.applink_address, selected=True,
                                  apply_modifiers=False, triangulate=False)

        file = open(importfile, "w")
        file.write("%s"%(checkname))
        file.write("\n%s"%(checkname))
        file.write("\n[%s]"%(coat3D.type))
        file.write("\n[TexOutput:%s]"%(folder_textures))
        file.close()
        group_index = -1.0

        for objekti in bpy.context.selected_objects:
            nimi = ''
            for koko in bpy.context.selected_objects:
                nimi += koko.name + ':::'
            objekti.coat3D.applink_group = nimi
            objekti.coat3D.applink_address = coa.applink_address
            objekti.coat3D.applink_name = coa.applink_name
            objekti.coat3D.applink_firsttime = True

        #coa.objecttime = str(os.path.getmtime(coa.applink_address))


        return {'FINISHED'}

class SCENE_OT_import(bpy.types.Operator):
    bl_idname = "import_applink.pilgway_3d_coat"
    bl_label = "import your custom property"
    bl_description = "import your custom property"
    bl_options = {'UNDO'}

    def invoke(self, context, event):

        coat3D = bpy.context.scene.coat3D
        coat = bpy.coat3D
        coat3D.exchangedir = set_exchange_folder()

        folder_objects,folder_textures = set_working_folders()

        Blender_folder = ("%s%sBlender"%(coat3D.exchangedir,os.sep))
        Blender_export = Blender_folder
        path3b_now = coat3D.exchangedir
        path3b_now += ('last_saved_3b_file.txt')
        Blender_export += ('%sexport.txt'%(os.sep))
        new_applink_address = 'False'
        new_object = False
        if(os.path.isfile(Blender_export)):
            obj_pathh = open(Blender_export)
            new_object = True
            for line in obj_pathh:
                new_applink_address = line
                break
            obj_pathh.close()

            for scene_objects in bpy.context.scene.objects:
                if(scene_objects.type == 'MESH'):
                    if(scene_objects.coat3D.applink_address == new_applink_address):
                        new_object = False

        if(new_object == False):

            #Blender -> 3DC -> Blender workflow

            for objekti in bpy.context.scene.objects:
                obj_coat = objekti.coat3D

                if(obj_coat.applink_address != '' and os.path.isfile(obj_coat.applink_address) and obj_coat.applink_skip == 'False'):
                    obj_coat.applink_skip = 'True'
                    objekti.select_set('SELECT')
                    exportfile = coat3D.exchangedir
                    path3b_n = coat3D.exchangedir
                    path3b_n += ('last_saved_3b_file.txt')
                    exportfile += ('%sexport.txt'%(os.sep))
                    if(os.path.isfile(exportfile)):
                        export_file = open(exportfile)
                        for line in export_file:
                            if line.rfind('.3b'):
                                objekti.coat3D.coatpath = line
                                coat['active_coat'] = line
                        export_file.close()
                        os.remove(exportfile)


                    obj_names = objekti.coat3D.applink_group
                    obj_list = obj_names.split(':::')
                    applinks = []
                    mat_list = []
                    for app_obj in obj_list:
                        pnimi = app_obj.lstrip()
                        listed = re.split(r'[:::]', pnimi)
                        for tobj in bpy.context.scene.collection.all_objects:
                            if(tobj.name == app_obj):
                                applinks.append(tobj)
                    if(obj_coat.objecttime != str(os.path.getmtime(obj_coat.applink_address))):
                        materials_old = bpy.data.materials.keys()
                        obj_coat.dime = objekti.dimensions
                        obj_coat.objecttime = str(os.path.getmtime(obj_coat.applink_address))
                        bpy.ops.wm.collada_import(filepath=obj_coat.applink_address)
                        bpy.ops.object.select_all(action='DESELECT')


                        materials_new = bpy.data.materials.keys()
                        new_ma = list(set(materials_new).difference(set(materials_old)))
                        proxy_index = -1
                        #bpy.data.materials.remove(bpy.data.materials[-1])
                        counter = 1
                        del_list = []

                        for obe in applinks:
                            counter += 1
                            obe.coat3D.applink_skip = 'True'
                            if(obe.coat3D.applink_address == objekti.coat3D.applink_address and obe.type == 'MESH'):
                                use_smooth = obe.data.polygons[0].use_smooth

                                if(obe.material_slots):
                                    act_mat = obe.active_material
                                    for obj_mat in obe.material_slots:
                                        mat_list.append(obj_mat.material)

                                #finds a object that was imported
                                if(obe.coat3D.applink_export == False):
                                    find_name = obe.name + '-mesh'
                                    find_name = find_name.replace('.', '_')
                                else:
                                    find_name = obe.name + '.001'
                                for allobjekti in bpy.context.scene.collection.all_objects:
                                    counter = 0

                                    if(allobjekti.name == find_name):
                                        obj_proxy = allobjekti
                                        del_list.append(allobjekti)
                                        break

                                bpy.ops.object.select_all(action='DESELECT')
                                obj_proxy.select_set('SELECT')

                                bpy.ops.object.select_all(action='TOGGLE')

                                if(coat3D.importlevel):
                                    obj_proxy.select = True
                                    obj_proxy.modifiers.new(name='temp',type='MULTIRES')
                                    obe.select = True
                                    bpy.ops.object.multires_reshape(modifier=multires_name)
                                    bpy.ops.object.select_all(action='TOGGLE')
                                    multires_on = False
                                else:

                                    #scene.objects.active = obj_proxy HACKKI
                                    obj_proxy.select_set('SELECT')

                                    obj_data = obe.data.id_data
                                    obe.data = obj_proxy.data.id_data
                                    if(bpy.data.meshes[obj_data.name].users == 0):
                                        obe.data.id_data.name = obj_data.name
                                        bpy.data.meshes.remove(obj_data)


                                objekti.select_set('SELECT')
                                if (obe.coat3D.applink_firsttime == True):
                                    obe.scale = (1, 1, 1)
                                    obe.rotation_euler = (0,0,0)
                                    obe.coat3D.applink_firsttime = False
                                bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
                                proxy_index -= 1
                                obe.material_slots[0].material = act_mat

                                if (use_smooth):
                                    for data_mesh in obe.data.polygons:
                                        data_mesh.use_smooth = True

                        bpy.ops.object.select_all(action='DESELECT')

                        for deleting in del_list:
                            deleting.select_set(action='SELECT')
                            bpy.ops.object.delete()
                        mat_index = 0
                        for obe in applinks:
                            bpy.data.materials.remove(bpy.data.materials[new_ma[mat_index]])
                            mat_index +=1

                    if(os.path.isfile(path3b_n)):
                        path3b_fil = open(path3b_n)
                        for lin in path3b_fil:
                            objekti.coat3D.path3b = lin
                        path3b_fil.close()
                        os.remove(path3b_n)

                    if(coat3D.importmesh and not(os.path.isfile(objekti.coat3D.applink_address))):
                        coat3D.importmesh = False

                    for obe in applinks:
                        obe.select_set('SELECT')
                        if(coat3D.importtextures):
                            is_new = False
                            tex.matlab(mat_list,obe,bpy.context.scene,is_new)
                        obe.select_set('DESELECT')

            for objekti in bpy.context.scene.objects:
                objekti.coat3D.applink_skip = 'False'

            for material in bpy.data.materials:
                if material.use_nodes == True:
                    for node in material.node_tree.nodes:
                        if (node.name).startswith('3DC'):
                            node.location = node.location

        else:

            # 3DC -> Blender workflow

            for old_obj in bpy.context.collection.objects:
                old_obj.coat3D.applink_old = True

            coat3D = bpy.context.scene.coat3D
            scene = context.scene
            Blender_folder = ("%s%sBlender"%(coat3D.exchangedir,os.sep))
            Blender_export = Blender_folder
            path3b_now = coat3D.exchangedir
            path3b_now += ('last_saved_3b_file.txt')
            Blender_export += ('%sexport.txt'%(os.sep))
            mat_list = []
            nimi = ''

            bpy.ops.wm.collada_import(filepath=new_applink_address)

            bpy.ops.object.select_all(action='DESELECT')
            for new_obj in bpy.context.collection.objects:

                if(new_obj.coat3D.applink_old == False):
                    nimi += new_obj.name + ':::'
                    new_obj.select_set('SELECT')
                    #bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
                    new_obj.rotation_euler = (0, 0, 0)
                    new_obj.select_set('DESELECT')
                    new_obj.coat3D.applink_address = new_applink_address
                    splittext = ntpath.basename(new_applink_address)
                    new_obj.coat3D.applink_name = splittext.split('.')[0]
                    new_obj.coat3D.applink_export = True
                    for material in bpy.data.materials:
                        if(new_obj.name == material.name):
                            new_obj.material_slots[0].material = material
                            break

                    # bpy.ops.object.transforms_to_deltas(mode='ROT')

                    mat_list.append(new_obj.material_slots[0].material)
                    is_new = True
                    tex.matlab(mat_list, new_obj, bpy.context.scene, is_new)

            for new_obj in bpy.context.collection.objects:
                if(new_obj.coat3D.applink_old == False):
                    new_obj.coat3D.applink_group = nimi
                    new_obj.coat3D.applink_old = True



            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            bpy.ops.object.select_all(action='DESELECT')

            os.remove(Blender_export)
            for material in bpy.data.materials:
                if material.use_nodes == True:
                    for node in material.node_tree.nodes:
                        if (node.name).startswith('3DC'):
                            node.location = node.location


        return {'FINISHED'}



from bpy import *
from mathutils import Vector, Matrix

# 3D-Coat Dynamic Menu
class VIEW3D_MT_Coat_Dynamic_Menu(bpy.types.Menu):
    bl_label = "3D-Coat Applink Menu"

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings
        layout.operator_context = 'INVOKE_REGION_WIN'
        coat3D = bpy.context.scene.coat3D
        Blender_folder = ("%s%sBlender"%(coat3D.exchangedir,os.sep))
        Blender_export = Blender_folder
        Blender_export += ('%sexport.txt'%(os.sep))

        ob = context
        if ob.mode == 'OBJECT':
            if(bpy.context.selected_objects):
                for ind_obj in bpy.context.selected_objects:
                    if(ind_obj.type == 'MESH'):
                        layout.active = True
                        break
                    layout.active = False

                if(layout.active == True):

                    layout.operator("import_applink.pilgway_3d_coat", text="Import")
                    layout.separator()

                    layout.operator("export_applink.pilgway_3d_coat", text="Export")
                    layout.separator()

                    layout.menu("VIEW3D_MT_ImportMenu")
                    layout.separator()

                    layout.menu("VIEW3D_MT_ExportMenu")
                    layout.separator()

                    layout.menu("VIEW3D_MT_ExtraMenu")
                    layout.separator()

                    if(len(bpy.context.selected_objects) == 1):
                        if(os.path.isfile(bpy.context.selected_objects[0].coat3D.path3b)):
                            layout.operator("import_applink.pilgway_3d_coat_3b", text="Load 3b")
                            layout.separator()

                    if(os.path.isfile(Blender_export)):

                        layout.operator("import3b_applink.pilgway_3d_coat", text="Bring from 3D-Coat")
                        layout.separator()
                else:
                    if(os.path.isfile(Blender_export)):
                        layout.active = True

                        layout.operator("import3b_applink.pilgway_3d_coat", text="Bring from 3D-Coat")
                        layout.separator()
            else:
                 if(os.path.isfile(Blender_export)):


                    layout.operator("import3b_applink.pilgway_3d_coat", text="Bring from 3D-Coat")
                    layout.separator()

class VIEW3D_MT_ImportMenu(bpy.types.Menu):
    bl_label = "Import Settings"

    def draw(self, context):
        layout = self.layout
        coat3D = bpy.context.scene.coat3D
        settings = context.tool_settings
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.prop(coat3D,"importmesh")
        layout.prop(coat3D,"importmod")
        layout.prop(coat3D,"smooth_on")
        layout.prop(coat3D,"importtextures")

class VIEW3D_MT_ExportMenu(bpy.types.Menu):
    bl_label = "Export Settings"

    def draw(self, context):
        layout = self.layout
        coat3D = bpy.context.scene.coat3D
        settings = context.tool_settings
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.prop(coat3D,"exportover")
        if(coat3D.exportover):
           layout.prop(coat3D,"exportmod")

class VIEW3D_MT_ExtraMenu(bpy.types.Menu):
    bl_label = "Extra"

    def draw(self, context):
        layout = self.layout
        coat3D = bpy.context.scene.coat3D
        settings = context.tool_settings
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("import_applink.pilgway_3d_deltex",text="Delete all Textures")
        layout.separator()

class ObjectCoat3D(PropertyGroup):
    objpath: StringProperty(
        name="Object_Path"
    )
    applink_address: StringProperty(
        name="Object_Applink_address"
    )
    applink_name: StringProperty(
        name="Applink object name"
    )
    applink_group: StringProperty(
        name="Applink group"
    )
    applink_skip: StringProperty(
        name="Object_Applink_Update",
        default="False"
    )
    applink_firsttime: BoolProperty(
        name="FirstTime",
        description="FirstTime",
        default=True
    )
    applink_old: BoolProperty(
        name="OldObject",
        description="Old Object",
        default=False
    )
    applink_export: BoolProperty(
        name="FirstTime",
        description="Object is from 3d-ocat",
        default=False
    )
    coatpath: StringProperty(
        name="Coat_Path"
    )
    objectdir: StringProperty(
        name="ObjectPath",
        subtype="FILE_PATH"
    )
    objecttime: StringProperty(
        name="ObjectTime",
        subtype="FILE_PATH"
    )
    texturefolder: StringProperty(
        name="Texture folder:",
        subtype="DIR_PATH"
    )
    path3b: StringProperty(
        name="3B Path",
        subtype="FILE_PATH"
    )
    export_on: BoolProperty(
        name="Export_On",
        description="Add Modifiers and export",
        default=False
    )
    dime: FloatVectorProperty(
        name="dime",
        description="Dimension"
    )
    loc: FloatVectorProperty(
        name="Location",
        description="Location"
    )
    rot: FloatVectorProperty(
        name="Rotation",
        description="Rotation",
        subtype='EULER'
    )
    sca: FloatVectorProperty(
        name="Scale",
        description="Scale"
    )


class SceneCoat3D(PropertyGroup):
    defaultfolder: StringProperty(
        name="FilePath",
        subtype="DIR_PATH",
    )
    cursor_loc: FloatVectorProperty(
        name="Cursor_loc",
        description="location"
    )
    exchangedir: StringProperty(
        name="FilePath",
        subtype="DIR_PATH"
    )
    exchangefolder: StringProperty(
        name="FilePath",
        subtype="DIR_PATH"
    )
    wasactive: StringProperty(
        name="Pass active object",
    )
    import_box: BoolProperty(
        name="Import window",
        description="Allows to skip import dialog",
        default=True
    )
    exchange_found: BoolProperty(
        name="Exchange Found",
        description="Alert if Exchange folder is not found",
        default=True
    )
    export_box: BoolProperty(
        name="Export window",
        description="Allows to skip export dialog",
        default=True
    )
    export_color: BoolProperty(
        name="Export color",
        description="Export color texture",
        default=True
    )
    export_spec: BoolProperty(
        name="Export specular",
        description="Export specular texture",
        default=True
    )
    export_normal: BoolProperty(
        name="Export Normal",
        description="Export normal texture",
        default=True
    )
    export_disp: BoolProperty(
        name="Export Displacement",
        description="Export displacement texture",
        default=True
    )
    export_position: BoolProperty(
        name="Export Source Position",
        description="Export source position",
        default=True
    )
    export_zero_layer: BoolProperty(
        name="Export from Layer 0",
        description="Export mesh from Layer 0",
        default=True
    )
    export_coarse: BoolProperty(
        name="Export Coarse",
        description="Export Coarse",
        default=True
    )
    exportfile: BoolProperty(
        name="No Import File",
        description="Add Modifiers and export",
        default=False
    )
    importmod: BoolProperty(
        name="Remove Modifiers",
        description="Import and add modifiers",
        default=False
    )
    exportmod: BoolProperty(
        name="Modifiers",
        description="Export modifiers",
        default=False
    )
    export_pos: BoolProperty(
        name="Remember Position",
        description="Remember position",
        default=True
    )
    importtextures: BoolProperty(
        name="Bring Textures",
        description="Import Textures",
        default=True
    )
    importlevel: BoolProperty(
        name="Multires. Level",
        description="Bring Specific Multires Level",
        default=False
    )
    exportover: BoolProperty(
        name="Export Obj",
        description="Import Textures",
        default=False
    )
    importmesh: BoolProperty(
        name="Mesh",
        description="Import Mesh",
        default=True
    )

    # copy location

    loca: FloatVectorProperty(
        name="location",
        description="Location",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )
    rota: FloatVectorProperty(
        name="location",
        description="Location",
        subtype="EULER",
        default=(0.0, 0.0, 0.0)
    )
    scal: FloatVectorProperty(
        name="location",
        description="Location",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )
    dime: FloatVectorProperty(
        name="dimension",
        description="Dimension",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )
    type: EnumProperty(
        name="Export Type",
        description="Different Export Types",
        items=(("ppp", "Per-Pixel Painting", ""),
               ("mv", "Microvertex Painting", ""),
               ("ptex", "Ptex Painting", ""),
               ("uv", "UV-Mapping", ""),
               ("ref", "Reference Mesh", ""),
               ("retopo", "Retopo mesh as new layer", ""),
               ("vox", "Mesh As Voxel Object", ""),
               ("alpha", "Mesh As New Pen Alpha", ""),
               ("prim", "Mesh As Voxel Primitive", ""),
               ("curv", "Mesh As a Curve Profile", ""),
               ("autopo", "Mesh For Auto-retopology", ""),
               ),
        default="ppp"
    )


classes = (
    #ObjectButtonsPanel,
    SCENE_PT_Main,
    SCENE_OT_export,
    SCENE_OT_import,
    VIEW3D_MT_Coat_Dynamic_Menu,
    VIEW3D_MT_ImportMenu,
    VIEW3D_MT_ExportMenu,
    VIEW3D_MT_ExtraMenu,
    ObjectCoat3D,
    SceneCoat3D,
    )

def register():
    bpy.coat3D = dict()
    bpy.coat3D['active_coat'] = ''
    bpy.coat3D['status'] = 0
    bpy.coat3D['kuva'] = 1

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Object.coat3D = PointerProperty(type=ObjectCoat3D)
    bpy.types.Scene.coat3D = PointerProperty(type=SceneCoat3D)

    kc = bpy.context.window_manager.keyconfigs.addon
    '''
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu2', 'Q', 'PRESS')
        kmi.properties.name = "VIEW3D_MT_Coat_Dynamic_Menu"
    '''


def unregister():

    import bpy
    from bpy.utils import unregister_class

    del bpy.types.Object.coat3D
    del bpy.types.Scene.coat3D
    del bpy.coat3D
    '''
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymapskeymaps['3D View']
        for kmi in km.keymap_items:
            if kmi.idname == '':
                if kmi.properties.name == "VIEW3D_MT_Coat_Dynamic_Menu":
                    km.keymap_items.remove(kmi)
                    break
    '''
    for cls in reversed(classes):
        unregister_class(cls)
