import os

class BatchMeshExportWorkbench (Workbench):

    MenuText = "Batch Mesh Export"
    ToolTip = "Tesselate and export multiple parts to stl files."
    import BatchMesh_utils as utils
    Icon = utils.getIconPath("workbench.svg")

    def Initialize(self):
        import BatchMesh
        self.list = ["BatchMeshExport_export", "BatchMeshExport_add"] # A list of command names created in the line above
        self.appendToolbar("Batch Mesh Commands",self.list) # creates a new toolbar with your commands

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands",self.list) # add commands to the context menu

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

Gui.addWorkbench(BatchMeshExportWorkbench())
