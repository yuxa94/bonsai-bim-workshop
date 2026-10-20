"""Reversible viewport-only CAD/IFC comparison. Never modifies IFC geometry/materials."""
from pathlib import Path
import json,math
import bpy
from mathutils import Quaternion,Vector
ROOT=Path(__file__).resolve().parents[1]
REFERENCE_DIR=ROOT/'jobs/unit25b/ghost'
NAME='25B · 원본 DWG 도면 (좌표 고정)'

def reference_settings():
    selected=getattr(bpy.context.scene,'cad_reference_map','')
    if not selected:
        try:
            import bonsai.tool as tool
            import ifcopenshell.util.element
            model=tool.Ifc.get()
            if model:
                selected=ifcopenshell.util.element.get_pset(model.by_type('IfcProject')[0],'CADOverlayReference','MappingPath') or ''
        except ImportError:pass
    path=Path(bpy.path.abspath(selected)) if selected else REFERENCE_DIR/'image-map.json'
    mapping=json.loads(path.read_text(encoding='utf8'))
    return path,mapping

def reference_name(mapping):
    return mapping.get('label','25B')+' · 원본 DWG 도면 (좌표 고정)'
def views():
    return [a for screen in bpy.data.screens for a in screen.areas if a.type=='VIEW_3D']
def opacity_update(self,context):
    for area in views():area.spaces.active.shading.xray_alpha=self.cad_ghost_opacity
def floors_update(self,context):
    if self.cad_ghost_enabled:enable()
def enable():
    try:
        import bonsai.tool as tool
    except ImportError:
        tool=None
    map_path,mapping=reference_settings();path=map_path.parent
    x1,y1,x2,y2=mapping['wcs_bounds_mm'];ox,oy=mapping['bim_origin_mm']
    name=reference_name(mapping)
    obj=bpy.context.scene.objects.get(name)
    if obj is None:
        obj=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(obj)
        obj.empty_display_type='IMAGE';obj.data=bpy.data.images.load(str(path/'original-plan.png'),check_existing=True)
        obj.empty_display_size=max(x2-x1,y2-y1)/1000
        obj.empty_image_offset=(-.5,-.5)
        obj.location=((x1+x2)/2000-ox/1000,(y1+y2)/2000-oy/1000,-.025)
        obj.empty_image_depth='BACK';obj.empty_image_side='DOUBLE_SIDED'
        obj.show_empty_image_perspective=True;obj.show_empty_image_orthographic=True
        obj.show_empty_image_only_axis_aligned=False;obj.color=(1,1,1,1)
        obj.hide_select=True;obj.hide_render=True;obj.lock_location=(True,True,True);obj.lock_rotation=(True,True,True);obj.lock_scale=(True,True,True)
        obj['source_wcs_bounds_mm']=mapping['wcs_bounds_mm'];obj['purpose']='Non-IFC display reference; original DWG exported through AutoCAD'
    obj['cad_overlay_reference']=True
    for other in bpy.context.scene.objects:
        if other.get('cad_overlay_reference') and other!=obj:other.hide_set(True)
    obj.hide_set(False)
    for candidate in bpy.context.scene.objects:
        entity=tool.Ifc.get_entity(candidate) if tool and tool.Ifc.get() else None
        if entity and entity.is_a('IfcSpace'):continue
        if entity and (entity.is_a('IfcSlab') or (entity.is_a('IfcCovering') and (entity.Name or '').startswith('바닥 /'))):
            if 'cad_previous_hidden' not in candidate:candidate['cad_previous_hidden']=candidate.hide_get()
            candidate.hide_set(not bpy.context.scene.cad_ghost_floors or candidate['cad_previous_hidden'])
        if candidate.type=='CURVE' and not entity:
            if 'cad_previous_hidden' not in candidate:candidate['cad_previous_hidden']=candidate.hide_get()
            candidate.hide_set(True)
    for area in views():
        space=area.spaces.active
        if 'cad_previous_shading' not in bpy.context.scene:
            bpy.context.scene['cad_previous_shading']=json.dumps({'type':space.shading.type,'color':space.shading.color_type,
                'xray':space.shading.show_xray,'alpha':space.shading.xray_alpha,'background':space.shading.background_type,
                'background_color':list(space.shading.background_color)})
        space.shading.type='SOLID';space.shading.color_type='SINGLE';space.shading.single_color=(.075,.43,.83)
        space.shading.show_xray=True;space.shading.xray_alpha=bpy.context.scene.cad_ghost_opacity
        space.shading.show_shadows=False;space.shading.show_cavity=False
        space.shading.background_type='VIEWPORT';space.shading.background_color=(.94,.94,.94)
        space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False
        space.overlay.show_extras=True;space.show_region_ui=True
    bpy.context.scene.cad_ghost_enabled=True
def disable():
    for obj in bpy.context.scene.objects:
        if obj.get('cad_overlay_reference') or obj.name==NAME:obj.hide_set(True)
    for candidate in bpy.context.scene.objects:
        if 'cad_previous_hidden' in candidate:candidate.hide_set(candidate['cad_previous_hidden'])
    previous=json.loads(bpy.context.scene.get('cad_previous_shading','{}'))
    for area in views():
        shading=area.spaces.active.shading
        shading.show_xray=previous.get('xray',False);shading.type=previous.get('type','SOLID');shading.color_type=previous.get('color','MATERIAL')
        shading.xray_alpha=previous.get('alpha',.5);shading.background_type=previous.get('background','THEME')
        if 'background_color' in previous:shading.background_color=previous['background_color']
        shading.show_shadows=True
    bpy.context.scene.cad_ghost_enabled=False
def viewpoint(mode):
    _,mapping=reference_settings()
    target=Vector(mapping.get('view_target_m',(1.81,4.15,.0)))
    eye=target+Vector((8,-13,23))
    for area in views():
        region=area.spaces.active.region_3d
        region.view_perspective='ORTHO';region.view_location=target
        region.view_distance=mapping.get('view_distance_m',14.0)
        region.view_rotation=Quaternion((1,0,0,0)) if mode=='TOP' else (target+Vector((0,0,.7))-eye).to_track_quat('-Z','Y')
        area.tag_redraw()
class CAD_OT_view(bpy.types.Operator):
    bl_idname='apartment_bim.cad_overlay';bl_label='CAD 겹쳐 보기'
    mode:bpy.props.EnumProperty(items=[('TOP','평면 대조',''),('AXON','입체 대조',''),('OFF','일반 보기','')])
    def execute(self,context):
        try:
            if self.mode=='OFF':disable()
            else:enable();viewpoint(self.mode)
        except (OSError,ValueError,KeyError) as error:
            self.report({'ERROR'},str(error))
            return {'CANCELLED'}
        return {'FINISHED'}
class CAD_PT_overlay(bpy.types.Panel):
    bl_label='원본 도면 · Ghost View';bl_idname='CAD_PT_overlay'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='CAD Overlay'
    def draw(self,context):
        layout=self.layout
        try:
            _,mapping=reference_settings();label=mapping.get('label','25B')
        except (OSError,ValueError,KeyError):label='참조를 선택하세요'
        layout.label(text=label+' 원본 DWG → DXF 도면',icon='IMAGE_REFERENCE')
        layout.prop(context.scene,'cad_reference_map',text='도면 매핑')
        layout.label(text='좌표 일치 · 1 mm = 0.001 m')
        layout.prop(context.scene,'cad_ghost_opacity',text='3D 불투명도',slider=True)
        layout.prop(context.scene,'cad_ghost_floors',text='바닥·슬래브도 표시')
        row=layout.row(align=True)
        row.operator('apartment_bim.cad_overlay',text='평면 대조').mode='TOP'
        row.operator('apartment_bim.cad_overlay',text='입체 대조').mode='AXON'
        layout.operator('apartment_bim.cad_overlay',text='일반 모델 보기').mode='OFF'
        layout.label(text='표시만 변경 · BIM 편집은 IFC 저장')
def register():
    if not hasattr(bpy.types.Scene,'cad_reference_map'):
        bpy.types.Scene.cad_reference_map=bpy.props.StringProperty(name='CAD reference mapping',subtype='FILE_PATH',description='image-map.json next to original-plan.png; empty uses IFC project reference or bundled25B')
    if not hasattr(bpy.types.Scene,'cad_ghost_opacity'):
        bpy.types.Scene.cad_ghost_opacity=bpy.props.FloatProperty(name='3D 불투명도',default=.22,min=.02,max=1.,update=opacity_update)
        bpy.types.Scene.cad_ghost_enabled=bpy.props.BoolProperty(default=False)
    if not hasattr(bpy.types.Scene,'cad_ghost_floors'):
        bpy.types.Scene.cad_ghost_floors=bpy.props.BoolProperty(default=False,update=floors_update)
    if not bpy.types.Operator.bl_rna_get_subclass_py('APARTMENT_BIM_OT_cad_overlay'):
        bpy.utils.register_class(CAD_OT_view)
    if not hasattr(bpy.types,'CAD_PT_overlay'):bpy.utils.register_class(CAD_PT_overlay)

def unregister():
    if hasattr(bpy.types.Scene,'cad_ghost_enabled') and bpy.context.scene.cad_ghost_enabled:disable()
    for registered in (getattr(bpy.types,'CAD_PT_overlay',None),
                       bpy.types.Operator.bl_rna_get_subclass_py('APARTMENT_BIM_OT_cad_overlay')):
        if registered:bpy.utils.unregister_class(registered)
    for name in ('cad_ghost_opacity','cad_ghost_enabled','cad_ghost_floors','cad_reference_map'):
        if hasattr(bpy.types.Scene,name):delattr(bpy.types.Scene,name)

def install():
    register()
    enable();viewpoint('TOP')
