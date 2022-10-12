import os
import BatchMesh_lib
MOD_PATH  = os.path.dirname(BatchMesh_lib.__file__)
ICONS_PATH= os.path.join(MOD_PATH, "resources/icons")

# get full path of icon directory
def getIconPath(icon_file_name):
    return os.path.join(ICONS_PATH, icon_file_name)
