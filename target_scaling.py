bl_info = {
    "name": "Target Scaling",
    "author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
    "modified_by": "Regis Nde Tene",
    "version": (1, 0, 6),
    "blender": (3, 5, 1),
    "location": "View 3D > Edit Mode > Tool Shelf",
    "description": "Scale your model to the correct target size",
    "warning": "",
    "wiki_url": "https://github.com/vvoovv/blender-tools/wiki/Target-Scaling",
    "tracker_url": "https://github.com/vvoovv/blender-tools/issues",
    "support": "COMMUNITY",
    "category": "3D View",
}

import bpy, bmesh, mathutils

class TargetScalingPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_label = "Target Scaling"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(context.scene, "target_length", text="Target Length")
        col.operator("edit.select_target_edge")
        col.separator()
        col.operator("edit.do_target_scaling")
        col.operator("edit.apply_target_scaling")
        col.operator("edit.copy_and_scale")

        # Add boolean properties for scaling in X, Y, Z
        col.prop(context.scene, "scale_x", text="Scale X")
        col.prop(context.scene, "scale_y", text="Scale Y")
        col.prop(context.scene, "scale_z", text="Scale Z")

def getSelectedEdgeLength(context):
    obj = context.active_object
    bm = bmesh.from_edit_mesh(obj.data)
    edge = bm.select_history.active
    l = -1
    if isinstance(edge, bmesh.types.BMEdge):
        v1 = obj.matrix_world @ edge.verts[0].co
        v2 = obj.matrix_world @ edge.verts[1].co
        l = (v1 - v2).length
        l = round(l, 5)
    return l

class SelectTargetEdge(bpy.types.Operator):
    bl_idname = "edit.select_target_edge"
    bl_label = "Select a target edge"
    bl_description = "Select a target edge"

    def execute(self, context):
        l = getSelectedEdgeLength(context)
        if l > 0:
            context.scene.target_length = l
            self.report({"INFO"}, "The target edge length is {}".format(l))
        else:
            self.report({"ERROR"}, "Select a single target edge!")
        return {"FINISHED"}

class DoTargetScaling(bpy.types.Operator):
    bl_idname = "edit.do_target_scaling"    
    bl_label = "Perform mesh scaling"
    bl_description = "Perform whole mesh scaling, so the selected edge will be equal to the target one."
    bl_options = {"UNDO"}

    def execute(self, context):
        l = getSelectedEdgeLength(context)
        if l > 0:
            if bpy.context.scene.unit_settings.system == 'IMPERIAL':
                unit_scale = 0.3048 # 1 meter is 3.28084 feet
            else:
                unit_scale = 1.0
            target_length_in_units = context.scene.target_length * unit_scale

            # Determine scaling factors based on user inputs
            scale_x = context.scene.scale_x
            scale_y = context.scene.scale_y
            scale_z = context.scene.scale_z

            # Initialize scale factors to 1.0
            scale_factors = [1.0, 1.0, 1.0]

            # Apply user-defined scaling factors
            if scale_x:
                scale_factors[0] = 1.0 / l * target_length_in_units
            if scale_y:
                scale_factors[1] = 1.0 / l * target_length_in_units
            if scale_z:
                scale_factors[2] = 1.0 / l * target_length_in_units

            # Apply the scaling
            bpy.ops.transform.resize(value=scale_factors)
            bpy.ops.mesh.select_all(action="DESELECT")
        else:
            self.report({"ERROR"}, "Select a single edge for target scaling!")
        return {"FINISHED"}

class ApplyTargetScaling(bpy.types.Operator):
    bl_idname = "edit.apply_target_scaling"    
    bl_label = "Apply target scaling"
    bl_description = "Apply target scaling to selected edges."
    bl_options = {"UNDO"}

    def execute(self, context):
        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            unit_scale = 0.3048 # 1 meter is 3.28084 feet
        else:
            unit_scale = 1.0
        target_length_in_units = context.scene.target_length * unit_scale

        # Determine scaling factors based on user inputs
        scale_x = context.scene.scale_x
        scale_y = context.scene.scale_y
        scale_z = context.scene.scale_z

        # Initialize scale factors to 1.0
        scale_factors = [1.0, 1.0, 1.0]

        # Apply user-defined scaling factors
        if scale_x:
            scale_factors[0] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units
        if scale_y:
            scale_factors[1] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units
        if scale_z:
            scale_factors[2] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units

        # Apply the scaling
        bpy.ops.transform.resize(value=scale_factors)
        bpy.ops.mesh.select_all(action="DESELECT")
        return {"FINISHED"}

class CopyAndScale(bpy.types.Operator):
    bl_idname = "edit.copy_and_scale"
    bl_label = "Copy and scale"
    bl_description = "Create a copy of the object and perform target scaling on it."
    bl_options = {"UNDO"}

    def execute(self, context):
        # Ensure we are in object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # duplicate the active object
        bpy.ops.object.duplicate()
        new_obj = context.active_object

        # switch to edit mode on the new object
        bpy.ops.object.mode_set(mode='EDIT')

        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            unit_scale = 0.3048 # 1 meter is 3.28084 feet
        else:
            unit_scale = 1.0
        target_length_in_units = context.scene.target_length * unit_scale

        # Determine scaling factors based on user inputs
        scale_x = context.scene.scale_x
        scale_y = context.scene.scale_y
        scale_z = context.scene.scale_z

        # Initialize scale factors to 1.0
        scale_factors = [1.0, 1.0, 1.0]

        # Apply user-defined scaling factors
        if scale_x:
            scale_factors[0] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units
        if scale_y:
            scale_factors[1] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units
        if scale_z:
            scale_factors[2] = 1.0 / getSelectedEdgeLength(context) * target_length_in_units

        # do scaling on the new object
        bpy.ops.transform.resize(value=scale_factors)

        # deselect everything
        bpy.ops.mesh.select_all(action="DESELECT")

        # switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # set origin to the center of object's bounding box
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        return {"FINISHED"}

def register():
    bpy.types.Scene.target_length = bpy.props.FloatProperty(
        name="Target Length",
        default=1.0,
        min=0.0001,
        description="The target edge length for scaling"
    )

    # Add boolean properties for scaling in X, Y, Z
    bpy.types.Scene.scale_x = bpy.props.BoolProperty(
        name="Scale X",
        default=True,
        description="Scale in the X direction"
    )
    
    bpy.types.Scene.scale_y = bpy.props.BoolProperty(
        name="Scale Y",
        default=True,
        description="Scale in the Y direction"
    )
    
    bpy.types.Scene.scale_z = bpy.props.BoolProperty(
        name="Scale Z",
        default=True,
        description="Scale in the Z direction"
    )

    classes = (TargetScalingPanel, SelectTargetEdge, DoTargetScaling, ApplyTargetScaling, CopyAndScale)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.target_length
    del bpy.types.Scene.scale_x
    del bpy.types.Scene.scale_y
    del bpy.types.Scene.scale_z
    
    classes = (TargetScalingPanel, SelectTargetEdge, DoTargetScaling, ApplyTargetScaling, CopyAndScale)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
