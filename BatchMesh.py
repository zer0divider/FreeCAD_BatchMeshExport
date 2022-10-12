import Mesh, Part
import MeshPart
import BatchMesh_utils as utils
import FreeCAD
import App
from FreeCAD import Base
import FreeCADGui as Gui
import os

class MeshExportProperty:
    prop_group="Mesh Export"
    def __init__(self, name, _type, default_value, doc):
        self.name = name
        self.default_value = default_value
        self.doc = doc
        self.type = _type
    
    # get this property from given object,
    # if it doesn't exist, it will be created automatically
    def getValue(self, o):
        try:
            v = o.getPropertyByName(self.name)
            return v
        except AttributeError:
            o.addProperty(self.type, self.name, self.prop_group, self.doc)
            setattr(o, self.name, self.default_value)
            return self.default_value

        
linear_deflection_prop = MeshExportProperty(
    "MeshLinearDeflection",
    "App::PropertyFloat",
    0.01,
    "Linear Deflection parameter of the standard tesselation algorithm.")

angular_deflection_prop = MeshExportProperty(
    "MeshAngularDeflection",
    "App::PropertyFloat",
    0.05,
    "Angular Deflection parameter of the standard tesselation algorithm.")

enable_export_prop = MeshExportProperty(
    "ExportSTL",
    "App::PropertyBool",
    True,
    "When enabled: Export each mesh to an stl file. When disabled: Only meshing is performed, no file export.")

input_label = "mesh_input"
output_label="mesh_output"

def log(s):
    FreeCAD.Console.PrintMessage("BatchMeshExporter: " + str(s)+"\n")
    pass

# create directories if not exist
def make_groups():
    # get active document
    doc = FreeCAD.activeDocument()

    # get input/output group
    input_group = doc.findObjects(Type="App::DocumentObjectGroup", Label=input_label)
    output_group = doc.findObjects(Type="App::DocumentObjectGroup", Label=output_label)

    # check whether groups exist, create if not
    if not input_group: 
        log("Creating group '"+input_label+"'")
        input_group = doc.addObject("App::DocumentObjectGroup", input_label);
    else:
        input_group = input_group[0]

    if not output_group: 
        log("Creating group '"+output_label+"'")
        output_group = doc.addObject("App::DocumentObjectGroup", output_label);
    else:
        output_group = output_group[0]

    # create properties
    linear_deflection_prop.getValue(input_group)
    angular_deflection_prop.getValue(input_group)
    enable_export_prop.getValue(input_group)

    return input_group, output_group

class CmdExport:
    subdir = "mesh_export"
    def GetResources(self):
        return {"Pixmap"  : utils.getIconPath("batch_mesh_export.svg"), # the name of a svg file available in the resources
                "Accel"   : "F5", # a default shortcut (optional)
                "MenuText": "Batch Mesh Export",
                "ToolTip" : "Tesselate and export all parts in 'mesh_input' group."}

    def Activated(self):
        # get active document
        doc = FreeCAD.activeDocument()

        input_group, output_group = make_groups();

        # get properties, create along the way if not exist
        linear_deflection = linear_deflection_prop.getValue(input_group)
        angular_deflection = angular_deflection_prop.getValue(input_group)
        enable_export = enable_export_prop.getValue(input_group)

        # clear all output mesh objects
        output_group.removeObjectsFromDocument()
        doc.recompute()

        # create directory to write files to
        dir_path = os.path.join(os.path.dirname(doc.getFileName()), self.subdir)
        os.makedirs(dir_path, exist_ok=True)

        # check for any objects in input
        input_objects = input_group.getSubObjects()
        if not input_objects:
            log("No objects in mesh_input, nothing to be done.")
            return

        # iterate all objects in input group,
        # for each: create a new Mesh Object and generate mesh from shape
        log("Converting to Mesh (LinearDeflection=%.3f, AngularDeflection=%.3f)"%(linear_deflection, angular_deflection))
        progress = Base.ProgressIndicator()
        progress.start("Meshing %d objects..."%(len(input_objects)), len(input_objects))
        meshes = []
        for o_str in input_objects:
            o = input_group.getSubObject(o_str, retType=0)
            doc_o = input_group.getSubObject(o_str, retType=1)
            label = doc_o.getPropertyByName("Label")
            name = label+"_mesh"
            m = doc.addObject("Mesh::Feature", name)
            log("  + %s -> %s"%(label, name))
            m.Mesh=MeshPart.meshFromShape(Shape=o, LinearDeflection=linear_deflection, AngularDeflection=angular_deflection, Relative=False)
            # hide newly created mesh if group is not visible
            if not output_group.ViewObject.isVisible():
                m.ViewObject.hide()
            output_group.addObject(m)
            m.ViewObject.update()
            meshes.append((label, name, m))

            try:
                progress.next(True)
            except(RuntimeError):
                log("Aborted.")
                doc.recompute()
                return


        progress.stop()

        if enable_export:
            progress.start("Exporting %d objects..."%(len(meshes)), len(meshes))
            log("Exporting Meshes to %s"%(dir_path))
            for m in meshes:
                # export to file
                file_name = m[0]+".stl"
                path = os.path.join(dir_path, file_name)
                log("  + %s -> %s"%(m[1], file_name))
                Mesh.export([m[2]], path);
                progress.next(True)

            progress.stop()

        log("Done.")
        return

    def IsActive(self):
        return True

class CmdAdd:
    def GetResources(self):
        return {"Pixmap"  : utils.getIconPath("add_to_batch.svg"), # the name of a svg file available in the resources
                "Accel"   : "Ctrl+Shift+A", # a default shortcut (optional)
                "MenuText": "Batch Add",
                "ToolTip" : "Add a link to the selected object to the "+input_label+" group."}

    def Activated(self):
        input_group, output_group = make_groups();

        # get selected object
        doc = FreeCAD.activeDocument()
        sel_obj = Gui.Selection.getSelection()
        for s in sel_obj:
            l = doc.addObject("App::Link", s.Label+"_export")
            l.setLink(s)
            input_group.addObject(l)
            if not input_group.ViewObject.isVisible():
                l.ViewObject.hide()


    def IsActive(self):
        sel_obj = Gui.Selection.getSelection()
        return len(sel_obj) > 0

Gui.addCommand("BatchMeshExport_export", CmdExport())
Gui.addCommand("BatchMeshExport_add", CmdAdd())
