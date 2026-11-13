"""Blender 4.3.2 / pinned Fast64: original marker and Tiny3D crate routes.

Run once per route: blender -b --python-exit-code 1 --python ... -- marker|blend|glb
FAST64_PATH and TINY3D_PATH select checked-out dependencies, never downloaded ROMs.
"""
import os, sys, json, hashlib, traceback, subprocess
from pathlib import Path
import bpy, addon_utils

ROOT = Path(__file__).resolve().parents[2]
route = sys.argv[sys.argv.index('--') + 1]
assert route in ('marker', 'blend', 'glb')
name = 'lab_' + route
out = ROOT / 'build/asset_lab/export'
out.mkdir(parents=True, exist_ok=True)
fast64_path = Path(os.environ.get('FAST64_PATH', ROOT.parent / 'fast64')).resolve()
tiny = Path(os.environ.get('TINY3D_PATH', ROOT.parent / 'vendor-tiny3d')).resolve()
assert bpy.app.version[:3] == (4, 3, 2), 'Use Blender 4.3.2'
for path, revision in [(fast64_path, 'b13010949567e4a2bf44ba3ccc18b06427243153'), (tiny, 'f2eccc3998967f1915be58d52f1c5bb6d5598a8c')]:
    assert subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip() == revision
sys.path.insert(0, str(fast64_path.parent))
report = {'route': route, 'blender': bpy.app.version_string, 'compiled': False, 'emulator_tested': False}
try:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('fast64', default_set=True, persistent=True)
    assert addon_utils.check('fast64')[1]
    from fast64.fast64_internal.f3d.f3d_material import createF3DMat
    if route == 'marker':
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([(0,0,0),(2,0,0),(2,1,0),(0,1,0),(.35,.25,1.5)], [],
                         [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2),(0,2,1)])
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        obj.data.uv_layers.new(name='UVMap')
        createF3DMat(obj, preset='sm64_shaded_solid')
    elif route == 'blend':
        src = tiny / 'examples/03_objects/assets/box.blend'
        bpy.ops.wm.open_mainfile(filepath=str(src))
        obj = bpy.data.objects.get('StoneFloor_F3d')
        assert obj and obj.type == 'MESH'
        # Preserve the existing F3D material. Ignore unrelated stale images/library meshes.
        for image in bpy.data.images:
            if image.name == 'crate00.ci8.png':
                image.filepath = str(src.parent / 'crate00.ci8.png')
                image.reload()
        report['source_sha256'] = hashlib.sha256(src.read_bytes()).hexdigest()
    else:
        src = tiny / 'examples/03_objects/assets/box.glb'
        bpy.ops.import_scene.gltf(filepath=str(src))
        obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
        report['source_sha256'] = hashlib.sha256(src.read_bytes()).hexdigest()
        # Generic GLB importer does not reconstruct Fast64 material properties.
        # Explicit static textured recipe; preserve UVs and source mesh, not opaque extras.
        obj.data.materials.clear()
        mat = createF3DMat(obj, preset='sm64_shaded_texture')
        mat.f3d_mat.tex0.tex = bpy.data.images.load(str(src.parent / 'crate00.ci8.png'), check_existing=True)
        mat.f3d_mat.tex0.tex_format = 'CI8'
        report['material_rebuilt'] = True
    if route == 'blend':
        # Source Tiny3D custom fog/subtractive combiner renders black in SM64.
        obj.data.materials.clear()
        mat = createF3DMat(obj, preset='sm64_shaded_texture')
        mat.f3d_mat.tex0.tex = bpy.data.images.load(str(src.parent / 'crate00.ci8.png'), check_existing=True)
        mat.f3d_mat.tex0.tex_format = 'CI8'
        report['material_rebuilt'] = True
        report['source_material_reuse'] = 'failed emulator visual check: black crate'
    scene = bpy.context.scene
    scene.gameEditorMode = 'SM64'
    scene.f3d_type = 'F3DEX2/LX2'
    scene.fast64.settings.dont_ask_color_management = True
    scene.fast64.sm64.export_type = 'C'
    scene.fast64.sm64.blender_to_sm64_scale = 100
    scene.fullTraceback = True
    scene.saveTextures = False
    scene.exportInlineF3D = False
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.name = name
    for m in obj.data.materials:
        m.name = name + '_material'
    obj.data.calc_loop_triangles()
    report['vertices'] = len(obj.data.vertices)
    report['triangles'] = len(obj.data.loop_triangles)
    report['bounds_local'] = [list(v) for v in obj.bound_box]
    report['scale'] = list(obj.scale)
    props = scene.fast64.sm64.combined_export
    props.custom_export_path = str(out)
    props.export_header_type = 'Custom'
    scene.DLName = name
    scene.DLExportisStatic = True
    scene.DLincludeChildren = False
    scene.DLSeparateTextureDef = False
    assert bpy.ops.object.sm64_export_dl() == {'FINISHED'}
    report['exported'] = True
    report['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/name).glob('*') if p.is_file()}
except Exception:
    report['error'] = traceback.format_exc()
    raise
finally:
    (out / (name + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print('ASSET_LAB_REPORT', json.dumps(report))
