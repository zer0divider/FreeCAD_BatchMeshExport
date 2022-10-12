install_path=~/.local/share/FreeCAD/Mod/BatchMeshExport
install_files=$(wildcard *.py) resources/
install:
	mkdir -p $(install_path)
	cp -rf $(install_files) $(install_path)/
