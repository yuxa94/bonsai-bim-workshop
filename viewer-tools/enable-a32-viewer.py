"""Register the existing A32 viewer for an already open single-floor IFC. Display only."""
from pathlib import Path
import importlib.util,sys
import bonsai.tool as tool
import ifcopenshell.util.element as element
root=Path(__file__).resolve().parent
model=tool.Ifc.get()
if model is None:raise RuntimeError('Open the downloaded A32 floor IFC in Bonsai first')
spec=importlib.util.spec_from_file_location('workshop_a32_floor_viewer',root/'scripts/a32_floor_viewer.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
module.register()
floors=[element.get_pset(s,'A32Storey','FloorId') for s in model.by_type('IfcBuildingStorey')]
if len(floors)==1 and floors[0] in module.FLOORS:
    import bpy
    bpy.context.scene.a32_review_floor=floors[0]
print('A32 viewer ready. N > 층별 검토. Select a floor actually present in this IFC.')
