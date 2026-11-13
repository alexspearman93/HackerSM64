"""LAB-106/107/108: existing Kenney props + glTF node animation adapter.
Run in Blender 4.3.2 with dependencies adjacent to the game checkout.
"""
import bpy,addon_utils,sys,json,hashlib,math,os,subprocess,struct
from pathlib import Path
from mathutils import Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT.parent
assert bpy.app.version[:3]==(4,3,2)
fast=Path(os.environ.get('FAST64_PATH',BASE/'fast64'))
assert subprocess.check_output(['git','-C',str(fast),'rev-parse','HEAD'],text=True).strip()=='b13010949567e4a2bf44ba3ccc18b06427243153'
kenney=Path(os.environ.get('KENNEY_PATH',BASE/'vendor-kenney'))
assert subprocess.check_output(['git','-C',str(kenney),'rev-parse','HEAD'],text=True).strip()=='3ddcc695adbba9fb918cf31b7c139b3f95b76910'
sys.path.insert(0,str(fast.parent))
route=sys.argv[sys.argv.index('--')+1]
assert route in ['tree','ramp','animated']
name='lab_'+route
src=kenney/'packs/platformer-kit'/('tree.glb' if route=='tree' else 'platform-ramp.glb') if route!='animated' else Path(os.environ.get('ANIMATED_PATH',BASE/'vendor-animated'))/'AnimatedCube.gltf'
expected = {'tree':'f04a16034071715cb8ac7889b3bb72add0afaa24eeb2f25869e2077935d9959a','ramp':'8c90140226147c830a22527fb32facc1ad61cef93d02dbd04e449d4cff9a9e80','animated':'59a3c451a5167b8ac4b59d61d4b94b2b7a215ee827efaed75629677a1217b552'}
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected[route]
if route=='animated':
    for f,h in {'AnimatedCube.bin':'82de770fc82b48a77a33bb26abd4d7e75620491b36ddf98e8dca69fa73dd798c','AnimatedCube_BaseColor.png':'0750d5a03c1bebc640571e309f66c6e88efbff2ef4c120619466a7014551bb9a'}.items():
        assert hashlib.sha256((src.parent/f).read_bytes()).hexdigest()==h
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('fast64',default_set=True,persistent=True)
from fast64.fast64_internal.f3d.f3d_material import createF3DMat
bpy.context.scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=str(src))
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.context.view_layer.objects.active=obj
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
report={'route':route,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source':str(src.name)}
out=ROOT/'build/asset_lab/export';out.mkdir(exist_ok=True,parents=True)
if route=='animated':
    # Read the glTF sampler directly: LINEAR quaternion tracks require SLERP.
    gltf=json.loads(src.read_text());track=gltf['animations'][0]
    assert len(track['channels'])==1 and track['channels'][0]['target']['path']=='rotation'
    sampler=track['samplers'][0];assert sampler.get('interpolation','LINEAR')=='LINEAR'
    def accessor(i, width):
        a=gltf['accessors'][i];v=gltf['bufferViews'][a['bufferView']]
        assert a['componentType']==5126 and 'sparse' not in a
        data=(src.parent/gltf['buffers'][v['buffer']]['uri']).read_bytes()
        return [struct.unpack_from('<'+'f'*width,data,v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',width*4)) for j in range(a['count'])]
    times=[v[0] for v in accessor(sampler['input'],1)]
    quats=[Quaternion((w,x,y,z)) for x,y,z,w in accessor(sampler['output'],4)]
    assert times==[0.0,1.0,2.0]
    angles=[]
    for frame in range(60):
        t=frame/30; i=0 if t<1 else 1
        R=quats[i].slerp(quats[i+1],(t-times[i])/(times[i+1]-times[i])).to_matrix()
        assert abs(R[1][1]-1)<1e-4 and abs(R[0][1])+abs(R[2][1])<1e-4
        angles.append(round(math.atan2(R[0][2],R[2][2])*32768/math.pi)%65536)
    report['animation']={'samples':60,'fps':30,'duration_seconds':2,'source_interpolation':'LINEAR quaternion / SLERP','target':'object yaw; not a skeletal adapter','yaw_u16':angles}
    obj.animation_data_clear();obj.rotation_mode='QUATERNION';obj.rotation_quaternion=(1,0,0,0)
    obj.location=(0,0,0);obj.scale=(1,1,1)
# Bake static object transform only; keep the animation cube centered.
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
mins=[min(v.co[i] for v in obj.data.vertices) for i in range(3)]
maxs=[max(v.co[i] for v in obj.data.vertices) for i in range(3)]
scale=600/(maxs[2]-mins[2]) if route=='tree' else 600/max(maxs[i]-mins[i] for i in (0,1)) if route=='ramp' else 100
if route!='animated':
    for v in obj.data.vertices: v.co.z-=mins[2]
report['target_scale']=scale
# Preserve source UVs/base-color image, reduce its resolution to fit 4KB TMEM.
images=[n.image for m in obj.data.materials if m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
assert images
image=images[0];report['source_texture_size']=list(image.size);image.scale(32,32)
obj.data.materials.clear();mat=createF3DMat(obj,preset='sm64_shaded_texture')
mat.name=name+'_material';mat.f3d_mat.tex0.tex=image;mat.f3d_mat.tex0.tex_format='RGBA16'
obj.name=name;obj.data.calc_loop_triangles()
report.update(vertices=len(obj.data.vertices),triangles=len(obj.data.loop_triangles),target_texture_size=[32,32],texture_format='RGBA16',warnings=['Base-color texture reduced to 32x32; metallic/roughness omitted.'])
# Matching world-space collision generated from the same normalized ramp mesh.
if route=='ramp':
    pts=[tuple(round(v.co[i]*scale) for i in (0,2,1)) for v in obj.data.vertices]
    pts=[(x,y,-z) for x,y,z in pts]
    lines=['const Collision lab_ramp_collision[] = {','COL_INIT(),',f'COL_VERTEX_INIT({len(pts)}),']
    lines += [f'COL_VERTEX({x},{y},{z}),' for x,y,z in pts]
    lines += [f'COL_TRI_INIT(SURFACE_NO_CAM_COLLISION,{len(obj.data.loop_triangles)}),']
    lines += ['COL_TRI(%d,%d,%d),'%tuple(t.vertices) for t in obj.data.loop_triangles]
    lines += ['COL_TRI_STOP(),COL_END(),};']
    (out/'ramp_collision.inc.c').write_text('\n'.join(lines)+'\n')
    report['bounds_target']=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    # Detailed planks produced gaps/sliding in emulator. Explicit gameplay wedge.
    (out/'ramp_collision_detailed.inc.c').write_text((out/'ramp_collision.inc.c').read_text())
    points=[(-292,0,-292),(-292,0,308),(-292,88,308),(292,0,308),(292,88,308),(292,0,-292),(292,333,-292),(-292,333,-292)]
    tris=[(0,1,2),(1,3,4),(1,4,2),(5,3,1),(5,1,0),(6,4,3),(6,3,5),(7,4,6),(7,2,4),(0,2,7),(7,6,5),(7,5,0)]
    lines=['const Collision lab_ramp_collision[] = {','COL_INIT(),COL_VERTEX_INIT(8),']
    lines += ['COL_VERTEX(%d,%d,%d),'%p for p in points]
    lines += ['COL_TRI_INIT(SURFACE_NOT_SLIPPERY,12),']
    lines += ['COL_TRI(%d,%d,%d),'%t for t in tris]
    lines += ['COL_TRI_STOP(),COL_END(),};']
    (out/'ramp_collision.inc.c').write_text('\n'.join(lines)+'\n')
    report['collision_recipe']={'type':'simplified wedge','front_lip':88,'back_height':333,'surface':'NOT_SLIPPERY','reason':'Detailed plank collision caused sliding/catching; first lip requires jump.'}

scene=bpy.context.scene;scene.gameEditorMode='SM64';scene.f3d_type='F3DEX2/LX2'
scene.fast64.settings.dont_ask_color_management=True;scene.fast64.sm64.export_type='C';scene.fast64.sm64.blender_to_sm64_scale=scale
scene.saveTextures=False;scene.exportInlineF3D=False;scene.DLName=name;scene.DLExportisStatic=True;scene.DLincludeChildren=False;scene.DLSeparateTextureDef=False
props=scene.fast64.sm64.combined_export;props.custom_export_path=str(out);props.export_header_type='Custom'
assert bpy.ops.object.sm64_export_dl()=={'FINISHED'}
report['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/name).glob('*')}
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
if route=='animated':
    (out/'animation.inc.c').write_text('/* Source glTF rotation sampled at 30Hz, 2-second loop. */\nstatic const u16 lab_animation_yaw[60] = {'+','.join(map(str,angles))+'};\n')
print('EXPANSION_REPORT',json.dumps(report))
