bl_info = {
    "name": "Matrix Text Generator",
    "author": "Ali Eissa",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Misc > Matrix generator",
    "description": "Tool for generating random matrix-like text",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"}

import bpy
import random
from bpy.app.handlers import persistent

updated = False

# util functions
def generate_default_charset():
    chars = []

    # Initialize characters for matrix effect
    
    # katakana characters
    chars += [chr(i) for i in range(12448, 12543)]
    # numbers
    chars += [str(i) for i in range(0, 9)]
    # spaces, 30 for probabilistic reasons
    chars += [" "] * 30
    # capital letters
    chars += [chr(i) for i in range(65, 90)]
    
    return ''.join(chars)

@persistent
def updateFrame(scene, *args, **kwargs):
        objs = [o for o in scene.objects if hasattr(o, 'matrixAddonConfig') and hasattr(o, 'matrixAddonData') ]

        random.seed(scene.frame_current)
        
        for obj in objs:
            if obj.matrixAddonConfig.animated and scene.frame_current % int(obj.matrixAddonConfig.every_frame) == int(float(obj.matrixAddonData.offset) * float(obj.matrixAddonConfig.every_frame)):
                
                freq = int(100 - obj.matrixAddonConfig.change_freq)
                chars = list(obj.matrixAddonConfig.charset)
                currentText = ""
                changeIndex = random.randint(0, freq)

                for c in range(0, len(obj.matrixAddonData.txt)):
                    if c >= changeIndex:
                        if obj.matrixAddonData.txt[c] != '\n' and obj.matrixAddonData.txt[c] != " ":
                            temp = chars[random.randint(0, len(chars) - 1)]
                            while temp == " ":
                                temp = chars[random.randint(0, len(chars) - 1)]
                            currentText += temp
                        else:
                            currentText += obj.matrixAddonData.txt[c]
                        changeIndex = random.randint(0, freq) + c
                    else:
                        currentText += obj.matrixAddonData.txt[c]

                obj.data.body = currentText

# Data classes
class MatrixAddonDataBlock(bpy.types.PropertyGroup):
    TMatrixAddon: bpy.props.StringProperty() # type: ignore
    txt: bpy.props.StringProperty() # type: ignore
    offset: bpy.props.FloatProperty() # type: ignore
    charset: bpy.props.StringProperty() # type: ignore


class MatrixAddonConfig(bpy.types.PropertyGroup):
    amount: bpy.props.IntProperty(
        name="Line Width",
        description="The width of each line of matrix text",
        default=3,
        min=0
    ) # type: ignore
    char_count: bpy.props.IntProperty(
        name="Line Count",
        description="The number of lines in the text",
        default=100,
        min=0
    ) # type: ignore
    every_frame: bpy.props.IntProperty(
        name="Animate Every",
        description="Animate every x frames",
        default=24,
        min=0
    ) # type: ignore
    change_freq: bpy.props.FloatProperty(
        name="Changing Frequency",
        description="How frequently characters change (percentage)",
        default=75,
        min=0.0,
        max=100.0,
        precision=0
    ) # type: ignore
    animated : bpy.props.BoolProperty(default=False, name="Animated") # type: ignore
    use_custom_charset : bpy.props.BoolProperty(default=False, name="Use Custom charset") # type: ignore
    charset : bpy.props.StringProperty(default=generate_default_charset()) # type: ignore

# Operator to generate matrix text
class MATRIX_OT_GENERATE(bpy.types.Operator):
    bl_label = "Generate Matrix Text"
    bl_idname = "matrix_addon.generate"
    
    def execute(self, context):
        obj = context.active_object
        if obj.type == "FONT":
            obj.data.body = ""

            width = obj.matrixAddonConfig.amount
            blancRange = random.randint(0, 15)  # right
            blancRange1 = random.randint(0, 15)  # left
            leftIndex = 0
            chars = list(obj.matrixAddonConfig.charset)

            for i in range(0, obj.matrixAddonConfig.char_count):
                for n in range(0, width):
                    if n < leftIndex:
                        obj.data.body += "  "
                    else:
                        obj.data.body += chars[random.randint(0, len(chars) - 1)]
                obj.data.body += '\n'

                if i >= blancRange:
                    width += random.randint(-1, 1)
                    blancRange = random.randint(0, 15) + i

                if i >= blancRange1:
                    leftIndex += random.randint(-1, 1)
                    blancRange1 = random.randint(0, 15) + i

            # Store the generated text in the object's custom data
            obj.matrixAddonData.txt = obj.data.body
            obj.matrixAddonData.TMatrixAddon = obj.name
            obj.matrixAddonData.offset = random.uniform(0, 1)

        return {'FINISHED'}

# Panel UI
class MATRIX_PT_PANEL(bpy.types.Panel):
    bl_idname = "MATRIX_PT_PANEL"
    bl_label = "Matrix Generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj and obj.type == "FONT":
            layout.label(text=f"Configuring: {obj.name}", icon='OBJECT_DATA')
            col = layout.column()
            
            col.prop(obj.matrixAddonConfig, "amount")

            col.prop(obj.matrixAddonConfig, "char_count")

            col.operator(MATRIX_OT_GENERATE.bl_idname)

            col.prop(obj.matrixAddonConfig, "animated")
            if obj.matrixAddonConfig.animated:
                col.prop(obj.matrixAddonConfig, "every_frame")
                col.prop(obj.matrixAddonConfig, "change_freq", slider=True)
            
            col.prop(obj.matrixAddonConfig, "use_custom_charset")
            if obj.matrixAddonConfig.use_custom_charset:
                col.prop(obj.matrixAddonConfig, "charset")
                

        else:
            layout.label(text="Select a text object to configure")


# Operator to reset animation
class MATRIX_OT_ClearAnim(bpy.types.Operator):
    bl_label = "Clear Animation"
    bl_idname = "matrix_addon.clear_anim"
    
    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if hasattr(obj, "matrixAddonData"):
                obj.data.body = obj.matrixAddonData.txt  # Restore original text
        return {'FINISHED'}

# Operator to assign selected objects for animation
class MATRIX_OT_ANIMATE(bpy.types.Operator):
    bl_label = "Animate Selected"
    bl_idname = "matrix_addon.animate"

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "FONT":
                obj.matrixAddonData.txt = obj.data.body
                obj.matrixAddonData.offset = random.uniform(0, 1)

        return {'FINISHED'}


# Register/Unregister Classes
classes = (
    MatrixAddonConfig,
    MatrixAddonDataBlock,
    MATRIX_OT_GENERATE,
    MATRIX_OT_ClearAnim,
    MATRIX_OT_ANIMATE,
    MATRIX_PT_PANEL
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.matrixAddonConfig = bpy.props.PointerProperty(type=MatrixAddonConfig)
    bpy.types.Object.matrixAddonData = bpy.props.PointerProperty(type=MatrixAddonDataBlock)
    bpy.app.handlers.frame_change_post.append(updateFrame)


def unregister():
    bpy.app.handlers.frame_change_post.remove(updateFrame)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.matrixAddonConfig
    del bpy.types.Object.matrixAddonData


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
