"""A32 floor isolation and registered original CAD viewer. Display changes only."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
FLOORS=['B5','B4','B3','B2','B1','01','02','PIT']+[f'{i:02}' for i in range(3,25)]+['RF','PH','PHR']

def reference_key(floor):
    if floor not in FLOORS:raise ValueError('Unknown A32 floor: '+floor)
    return '05-23' if floor.isdigit() and 5<=int(floor)<=23 else floor

def image_placement(mapping,elevation):
    x1,y1,x2,y2=mapping['wcs_bounds_mm'];ox,oy=mapping['bim_origin_mm']
    return ((x1+x2)/2000-ox/1000,(y1+y2)/2000-oy/1000,elevation-.025),max(x2-x1,y2-y1)/1000

STATE={}
try:import bpy
except ImportError:bpy=None

if bpy:
    from mathutils import Vector,Quaternion
    import bonsai.tool as tool
    import ifcopenshell.util.element as element

    def views():
        return [a for screen in bpy.data.screens for a in screen.areas if a.type=='VIEW_3D']

    def snapshot():
        if STATE:return
        STATE['file']=tool.Ifc.get_path()
        STATE['hidden']={o.name:o.hide_get() for o in bpy.context.scene.objects}
        STATE['views']=[]
        for a in views():
            s=a.spaces.active;r=s.region_3d
            attrs=['type','color_type','single_color','show_xray','xray_alpha','show_shadows','show_cavity','background_type','background_color']
            STATE['views'].append((a,{k:(tuple(v) if hasattr(v,'__len__') and not isinstance(v,str) else v) for k in attrs if (v:=getattr(s.shading,k)) is not None},
                (r.view_location.copy(),r.view_rotation.copy(),r.view_distance,r.view_perspective),
                {k:getattr(s.overlay,k) for k in ['show_floor','show_axis_x','show_axis_y','show_extras']}))

    def source_object(floor,elev):
        key=reference_key(floor)
        mapping_path=ROOT/'output/a32-residential/references-v003'/key/'image-map.json'
        m=json.loads(mapping_path.read_text(encoding='utf8'))
        name='A32 CAD reference · '+key
        obj=bpy.data.objects.get(name)
        if obj is None:
            obj=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(obj)
            obj.empty_display_type='IMAGE';obj.data=bpy.data.images.load(str(mapping_path.parent/'original-plan.png'),check_existing=True)
            obj.empty_image_offset=(-.5,-.5);obj.empty_image_depth='BACK';obj.empty_image_side='DOUBLE_SIDED'
            obj.show_empty_image_perspective=True;obj.show_empty_image_orthographic=True
            obj.show_empty_image_only_axis_aligned=False;obj.hide_select=True;obj.hide_render=True
            obj.lock_location=(True,True,True);obj.lock_rotation=(True,True,True);obj.lock_scale=(True,True,True)
            obj['a32_floor_reference']=True;obj['mapping_path']=str(mapping_path)
            obj['wcs_bounds_mm']=m['wcs_bounds_mm'];obj['bim_origin_mm']=m['bim_origin_mm']
        obj.location,obj.empty_display_size=image_placement(m,elev)
        if obj.get('mapping_path')!=str(mapping_path):
            obj.data=bpy.data.images.load(str(mapping_path.parent/'original-plan.png'),check_existing=True)
            obj['mapping_path']=str(mapping_path)
        obj.color=(1,1,1,1)
        return obj

    def apply(mode=None):
        scene=bpy.context.scene;f=tool.Ifc.get()
        if not f:raise ValueError('Open the A32 residential IFC first')
        floor=scene.a32_review_floor
        stores={element.get_pset(s,'A32Storey','FloorId'):s for s in f.by_type('IfcBuildingStorey')}
        if floor not in stores:raise ValueError('This IFC does not contain floor '+floor)
        if mode:scene.a32_review_mode=mode
        mode=scene.a32_review_mode
        if STATE and STATE['file']!=tool.Ifc.get_path():restore()
        snapshot();st=stores[floor];elev=st.Elevation
        ref=source_object(floor,elev) if mode in ['GHOST','SOURCE'] else None
        for obj in bpy.context.scene.objects:
            e=tool.Ifc.get_entity(obj)
            if obj.get('a32_floor_reference'):hidden=obj!=ref
            elif obj.get('a32_ramp_curve'):hidden=True
            elif not e and obj.type in ['CAMERA','LIGHT']:hidden=True
            elif e and e.is_a('IfcTypeObject'):hidden=True
            elif e and e.is_a('IfcProduct'):
                owner=element.get_container(e,ifc_class='IfcBuildingStorey')
                if e.is_a('IfcBuildingStorey'):owner=e
                hidden=owner!=st or mode=='SOURCE'
                floor_finish=e.is_a('IfcCovering') and (element.get_predefined_type(e)=='FLOORING' or '바닥' in (e.Name or ''))
                if mode=='GHOST' and not scene.a32_review_slabs and (e.is_a('IfcSlab') or floor_finish or e.is_a('IfcSpace')):hidden=True
            else:continue
            if obj.hide_get()!=hidden:obj.hide_set(hidden)
        target=Vector((21,14 if floor.startswith('B') or floor=='01' else 18,elev+1));eye=target+Vector((35,-48,60))
        for a in views():
            s=a.spaces.active;r=s.region_3d
            s.shading.type='SOLID';s.shading.color_type='SINGLE' if mode=='GHOST' else 'MATERIAL'
            s.shading.single_color=(.05,.36,.9);s.shading.show_xray=mode=='GHOST'
            s.shading.xray_alpha=scene.a32_review_opacity;s.shading.show_shadows=False
            s.shading.background_type='VIEWPORT';s.shading.background_color=(1,1,1)
            s.overlay.show_floor=False;s.overlay.show_axis_x=False;s.overlay.show_axis_y=False;s.overlay.show_extras=True
            r.view_location=target;r.view_distance=90 if floor in ['B5','B4','B3','B2','B1','01','02','PIT'] else 63;r.view_perspective='ORTHO'
            r.view_rotation=(target-eye).to_track_quat('-Z','Y') if mode=='AXON' else Quaternion((1,0,0,0))
            s.show_region_ui=True;a.tag_redraw()
        scene.a32_review_active=True

    def restore():
        for name,hidden in STATE.get('hidden',{}).items():
            obj=bpy.data.objects.get(name)
            if obj and obj.hide_get()!=hidden:obj.hide_set(hidden)
        for obj in bpy.context.scene.objects:
            if obj.get('a32_floor_reference') or obj.get('a32_ramp_curve'):obj.hide_set(True)
        for a,shading,view,overlay in STATE.get('views',[]):
            try:
                s=a.spaces.active
                for k,v in shading.items():setattr(s.shading,k,v)
                for k,v in overlay.items():setattr(s.overlay,k,v)
                r=s.region_3d;r.view_location,r.view_rotation,r.view_distance,r.view_perspective=view
                a.tag_redraw()
            except ReferenceError:pass
        STATE.clear();bpy.context.scene.a32_review_active=False

    def floor_changed(self,context):
        if self.a32_review_active:
            try:apply()
            except (ValueError,OSError) as err:print('A32 viewer:',err)

    def opacity_changed(self,context):
        if self.a32_review_active:
            for a in views():a.spaces.active.shading.xray_alpha=self.a32_review_opacity

    class A32_OT_review(bpy.types.Operator):
        bl_idname='a32.floor_review';bl_label='A32 층별 검토'
        action:bpy.props.StringProperty(default='GHOST')
        def execute(self,context):
            try:
                if self.action=='ALL':restore()
                elif self.action in ['NEXT','PREV']:
                    i=FLOORS.index(context.scene.a32_review_floor)
                    context.scene.a32_review_floor=FLOORS[max(0,min(len(FLOORS)-1,i+(1 if self.action=='NEXT' else -1)))]
                    if not context.scene.a32_review_active:apply()
                else:apply(self.action)
            except (ValueError,OSError,KeyError) as err:
                self.report({'ERROR'},str(err));return {'CANCELLED'}
            return {'FINISHED'}

    class A32_PT_review(bpy.types.Panel):
        bl_label='A32 · 층별 도면 검토';bl_idname='A32_PT_review'
        bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='층별 검토'
        def draw(self,context):
            s=context.scene;l=self.layout
            l.prop(s,'a32_review_floor',text='검토 층')
            row=l.row(align=True)
            row.operator('a32.floor_review',text='이전 층',icon='TRIA_DOWN').action='PREV'
            row.operator('a32.floor_review',text='다음 층',icon='TRIA_UP').action='NEXT'
            l.label(text='원본: '+reference_key(s.a32_review_floor)+' 평면도')
            row=l.row(align=True)
            row.operator('a32.floor_review',text='층 평면').action='TOP'
            row.operator('a32.floor_review',text='층 3D · Isolate').action='AXON'
            l.operator('a32.floor_review',text='원본 도면 + 모델 겹쳐 비교',icon='IMAGE_REFERENCE').action='GHOST'
            l.operator('a32.floor_review',text='원본 도면만 보기').action='SOURCE'
            l.prop(s,'a32_review_opacity',text='모델 불투명도',slider=True)
            l.prop(s,'a32_review_slabs',text='비교 시 바닥·공간 표시')
            l.operator('a32.floor_review',text='전체동 · 이전 표시 복원',icon='LOOP_BACK').action='ALL'
            l.label(text='치수·문자 포함 원본 CAD / 좌표 고정')
            l.label(text='표시 전용 · IFC 형상과 재료 유지')

    def register():
        if hasattr(bpy.types,'A32_PT_review'):return
        bpy.types.Scene.a32_review_floor=bpy.props.EnumProperty(items=[(s,s+'층' if s.isdigit() else s,'') for s in FLOORS],default='05',update=floor_changed)
        bpy.types.Scene.a32_review_mode=bpy.props.StringProperty(default='GHOST')
        bpy.types.Scene.a32_review_active=bpy.props.BoolProperty(default=False)
        bpy.types.Scene.a32_review_opacity=bpy.props.FloatProperty(default=.22,min=.02,max=1,update=opacity_changed)
        bpy.types.Scene.a32_review_slabs=bpy.props.BoolProperty(default=False,update=floor_changed)
        for cls in [A32_OT_review,A32_PT_review]:bpy.utils.register_class(cls)

    def unregister():
        restore()
        for cls in [A32_PT_review,A32_OT_review]:bpy.utils.unregister_class(cls)
        for s in ['floor','mode','active','opacity','slabs']:delattr(bpy.types.Scene,'a32_review_'+s)
