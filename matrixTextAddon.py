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


updated = False

mydata = None


txtObjs = []
originalTxt = []
randOffset = []

def updataData() :
    global updated
    global txtObjs
    global originalTxt
    global randOffset 
    #objtext = mydata.TMatrixAddon.add()
    #txttemp = mydata.txt.add()
    #offtemp = mydata.offset.add()
    
    for i in range(0, len(bpy.context.scene.matrixAddonData)):
        txtObjs.append(bpy.data.objects.get(bpy.context.scene.matrixAddonData[i].TMatrixAddon))
        originalTxt.append(bpy.context.scene.matrixAddonData[i].txt)
        randOffset.append(bpy.context.scene.matrixAddonData[i].offset)
    
    updated = True


class MatrixAddonDataBlock(bpy.types.PropertyGroup):
    # annotation
    TMatrixAddon : bpy.props.StringProperty()
    txt : bpy.props.StringProperty()
    offset : bpy.props.FloatProperty()
    
class MatrixAddonConfig(bpy.types.PropertyGroup):
    amount : bpy.props.IntProperty \
      (
        name = "line width",
        description = "My description",
        default = 3,
        min = 0
      )
    characterCount : bpy.props.IntProperty \
      (
        name = "Line Count",
        description = "My description",
        default = 100, 
        min = 0
      )
    everyframe : bpy.props.IntProperty \
      (
        name = "Animate every",
        description = "animate every x frames",
        default = 24,
        min = 0
      )
    changeFreq : bpy.props.FloatProperty \
      (
        name = "Changing frequency",
        description = "how much characters to change during ",
        default = 75,
        min = 0.0,
        max = 100.0, 
        precision = 0
      )
    


class MATRIX_OT_GENERATE(bpy.types.Operator):
    bl_label = "Generate matrix text"
    bl_idname = "matrix_addon.generate"
    
    chars = []
    
    for i in range (12448, 12543): #katana japanese characters
        chars += chr(i)
    
    for i in range (0, 9): #numbers
        chars += str(i)

    for i in range (0, 30): #spaces test
        chars += " "
        
    for i in range (65, 90): #capital letters
        chars += chr(i)


    def execute(self, context):
        obj = context.active_object
        if obj.type == "FONT":
            obj.data.body = ""
            
            width = int(context.scene.matrixAddonConfig.amount)
            blancRange = random.randint(0, 15) #right
            blancRange1 = random.randint(0, 15)  #left 
            blancRange2 = random.randint(0, 15)  #mid
            rmLlineIndex = random.randint(0, width)
            leftIndex = 0
            
            for i in range (0, int(context.scene.characterCount.characterCount)):
                for n in range (0, width):
                    if n < leftIndex:
                        obj.data.body += "  "
                    else:
                        obj.data.body += self.chars[random.randint(0, len(self.chars) - 1)]
                obj.data.body += '\n'
                
                if i >= blancRange:
                    width += random.randint(-1, 1)
                    blancRange = random.randint(0, 15) + i
                
                if i >= blancRange1:
                    leftIndex += random.randint(-1, 1)
                    blancRange1 = random.randint(0, 15) + i
                    
            #originalTxt.append(obj.data.body)
            #print("Hello World")
        return {'FINISHED'}
    
    
    @classmethod
    def updateFrame(self, context):
        global txtObjs
        global originalTxt
        global randOffset
        
        freq = int(100 - context.scene.matrixAddonConfig.changeFreq)
                
        random.seed(bpy.context.scene.frame_current)  # current frame as the random seed
        for n in range(0, len(txtObjs)):
            if bpy.context.scene.frame_current % int(context.scene.characterCount.everyframe) == int(float(randOffset[n]) * float(context.scene.characterCount.everyframe)):
                currentText = ""
                
                changeIndex = random.randint(0, freq)  #edit max value to edit frequency, less = more frequency of changes
                #i = 0
                for c in range(0, len(originalTxt[n])):
                    
                    if c >= changeIndex:
                        if originalTxt[n][c] != '\n' and originalTxt[n][c] != " ":
                            temp = MATRIX_OT_GENERATE.chars[random.randint(0, len(MATRIX_OT_GENERATE.chars) - 1)]
                            while temp == " ":
                                temp = MATRIX_OT_GENERATE.chars[random.randint(0, len(MATRIX_OT_GENERATE.chars) - 1)]
                                print('here1')
                            
                            currentText += temp
                        else:
                            currentText += originalTxt[n][c]
                        changeIndex = random.randint(0, freq) + c
                        
                    else:
                        currentText += originalTxt[n][c]
                    #i += 1       
                txtObjs[n].data.body = currentText
        return {'FINISHED'}
        
class MATRIX_OT_ClearAnim(bpy.types.Operator):
    bl_label = "Clear Animation"
    bl_idname = "matrix_addon.clear_anim"
    bl_description = ""

    def execute(self, context):
        global txtObjs
        global originalTxt
        global randOffset

        for i in range(0, len(txtObjs)):
            try:
                txtObjs[i].data.body = originalTxt[i]
            except:
                print("nah")
        txtObjs = []
        originalTxt = []
        randOffset = []
        
        context.scene.matrixAddonData = bpy.props.CollectionProperty(type=MatrixAddonDataBlock)
        
        return {'FINISHED'}
    

class MATRIX_OT_ANIMATE(bpy.types.Operator):
    bl_label = "Animate Selected"
    bl_idname = "matrix_addon.animate"
    bl_description = ""
    
    def execute(self, context):
        self.assignSelected(context)
        
        return {'FINISHED'}
    
    def assignSelected(self, context):
        global txtObjs
        global originalTxt
        global randOffset
        temp = [ o for o in bpy.context.selected_objects if o.select_get() and o.type == "FONT" ]
        #if len(txtObjs) == 0:
        txtObjs = temp
        originalTxt = []
        randOffset = []

        for i, txt in enumerate(temp):
            originalTxt.append(txt.data.body)
            randOffset.append(random.uniform(0, 1))     #TMatrixAddon = bpy.types.PointerProperty()     txt = bpy.types.StringProperty()   offset = bpy.types.FloatProperty()
            if i < len(context.scene.matrixAddonData):
                mydata = context.scene.matrixAddonData[i]
            else:
                mydata = context.scene.matrixAddonData.add()
            mydata.TMatrixAddon = txt.name
            mydata.txt = txt.data.body
            mydata.offset = random.uniform(0, 1)
        # clear extra entries
        if len(context.scene.matrixAddonData) > len(temp):
            for i in range(len(temp), len(context.scene.matrixAddonData)):
                context.scene.matrixAddonData.remove(i)


class MATRIX_PT_PANEL(bpy.types.Panel):
    #Creates a Panel in the MatrixAddon properties window
    bl_idname = "matrix_addon.panel"
    bl_label = "Matrix generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = "objectmode"
    
    bl_category = "Misc"
    

    # def draw_header(self, context):
    #     layout = self.layout
    #     #layout.label(text="Matrix Generator")

    def draw(self, context):
        layout = self.layout

        #obj = context.MatrixAddon

        #row = layout.row()
        #row.label(text="Active MatrixAddon is: " + obj.type)
        #row = layout.row()
        #row.prop(obj, "type")

        row = layout.row()   #line width
        row.prop(context.scene.matrixAddonConfig, "amount")
        
        row = layout.row()   # amount of chars
        row.prop(context.scene.matrixAddonConfig, "characterCount")

        row = layout.row()
        row.operator(MATRIX_OT_GENERATE.bl_idname)
        
        row = layout.row()
        row.operator(MATRIX_OT_ANIMATE.bl_idname, text="Animate Selected")
        
        row = layout.row()   # animate every x frames
        row.prop(context.scene.matrixAddonConfig, "everyframe")
        
        row = layout.row()   # changing frequency
        row.prop(context.scene.matrixAddonConfig, "changeFreq", slider=True)

        row = layout.row()
        row.operator(MATRIX_OT_ClearAnim.bl_idname, text="Restore all")
    
        if updated == False:
            updataData()
        
classes = (
    MatrixAddonConfig,
    MatrixAddonDataBlock,
    MATRIX_OT_ClearAnim,
    MATRIX_OT_GENERATE,
    MATRIX_OT_ANIMATE,
    MATRIX_PT_PANEL
    )    


def register():
    global mydata

    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.matrixAddonConfig = bpy.props.PointerProperty(type=MatrixAddonConfig)
    bpy.types.Scene.matrixAddonData = bpy.props.CollectionProperty(type=MatrixAddonDataBlock)
    bpy.app.handlers.frame_change_post.append(MATRIX_OT_GENERATE.updateFrame)
    #mydata = bpy.types.Scene.matrixAddonData.add()

def unregister():
    bpy.app.handlers.frame_change_post.remove(MATRIX_OT_GENERATE.updateFrame)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del(bpy.types.Scene.matrixAddonData)


if __name__ == "__main__":
    print("registering")
    try:
        unregister()
    except:
        pass
    register()
