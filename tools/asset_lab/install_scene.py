"""Generate an original test courtyard and install already exported assets.

Stage 0=empty courtyard, 1=marker, 2=Blender crate, 3=GLB comparison.
Only the dedicated asset-lab checkout may run this script.
"""
from pathlib import Path
import argparse, shutil, json, subprocess

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--stage', type=int, choices=range(4), default=3)
args = parser.parse_args()
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip() == 'asset-lab'
dest = ROOT / 'levels/bob/asset_lab'
dest.mkdir(exist_ok=True)
names = ['lab_marker','lab_blend','lab_glb'][:args.stage]
for name in names:
    shutil.copytree(ROOT/'build/asset_lab/export'/name, dest/name, dirs_exist_ok=True)

# Vertex-colored checker floor, with three colored station pads. All authored here.
quads=[]
for x in range(-1600,1600,400):
    for z in range(-1200,1600,400):
        c=110 if (x//400+z//400)%2 else 135
        quads.append(([(x,0,z),(x,0,z+400),(x+400,0,z+400),(x+400,0,z)],(c,c,c)))
for x,c in [(-500,(160,65,65)),(0,(65,145,85)),(500,(65,100,180))]:
    quads.append(([(x-150,1,-150),(x-150,1,150),(x+150,1,150),(x+150,1,-150)],c))
lines=['/* Original Asset Lab courtyard. */','Vtx lab_floor_vertices[] = {']
for verts,c in quads:
    for x,y,z in verts: lines.append('    {{{%d,%d,%d},0,{0,0},{%d,%d,%d,255}}},'%(x,y,z,*c))
lines += ['};','Gfx lab_floor_dl[] = {','gsDPPipeSync(),','gsSPClearGeometryMode(G_LIGHTING),','gsDPSetCombineMode(G_CC_SHADE,G_CC_SHADE),','gsSPTexture(0,0,0,G_TX_RENDERTILE,G_OFF),']
for i in range(len(quads)):
    lines += [f'gsSPVertex(lab_floor_vertices+{4*i},4,0),','gsSP2Triangles(0,1,2,0,0,2,3,0),']
lines += ['gsDPPipeSync(),','gsSPSetGeometryMode(G_LIGHTING),','gsSPEndDisplayList(),','};']
(dest/'floor.inc.c').write_text('\n'.join(lines)+'\n')
(dest/'collision.inc.c').write_text('''const Collision lab_floor_collision[] = {
COL_INIT(), COL_VERTEX_INIT(4),
COL_VERTEX(-1600,0,-1200), COL_VERTEX(-1600,0,1600),
COL_VERTEX(1600,0,1600), COL_VERTEX(1600,0,-1200),
COL_TRI_INIT(SURFACE_DEFAULT,2), COL_TRI(0,1,2), COL_TRI(0,2,3),
COL_TRI_STOP(), COL_END(),
};
''')
headers=['extern Gfx lab_floor_dl[];','extern const Collision lab_floor_collision[];','extern const GeoLayout lab_area_geo[];']
models=[]
geos=[]
for name in names:
    headers += [(dest/name/'header.h').read_text(),f'extern const GeoLayout {name}_geo[];']
    models.append(f'#include "levels/bob/asset_lab/{name}/model.inc.c"')
    geos.append(f'const GeoLayout {name}_geo[] = {{ GEO_NODE_START(), GEO_OPEN_NODE(), GEO_DISPLAY_LIST(LAYER_OPAQUE,{name}_{name}_mesh), GEO_CLOSE_NODE(), GEO_END(), }};')
(dest/'header.h').write_text('\n'.join(headers)+'\n')
(dest/'models.inc.c').write_text('\n'.join(models)+'\n')
(dest/'geo.inc.c').write_text('\n'.join(geos)+'''
const GeoLayout lab_area_geo[] = {
GEO_NODE_SCREEN_AREA(10,SCREEN_CENTER_X,SCREEN_CENTER_Y,SCREEN_CENTER_X,SCREEN_CENTER_Y),
GEO_OPEN_NODE(),
 GEO_ZBUFFER(0), GEO_OPEN_NODE(), GEO_NODE_ORTHO(100), GEO_OPEN_NODE(),
 GEO_BACKGROUND_COLOR(0x294B), GEO_CLOSE_NODE(), GEO_CLOSE_NODE(),
 GEO_ZBUFFER(1), GEO_OPEN_NODE(),
 GEO_CAMERA_FRUSTUM_WITH_FUNC(45,100,10000,geo_camera_fov), GEO_OPEN_NODE(),
 GEO_CAMERA(CAMERA_MODE_8_DIRECTIONS,0,1200,2200,0,0,0,geo_camera_main), GEO_OPEN_NODE(),
 GEO_DISPLAY_LIST(LAYER_OPAQUE,lab_floor_dl), GEO_RENDER_OBJ(),
 GEO_CLOSE_NODE(), GEO_CLOSE_NODE(), GEO_CLOSE_NODE(),
GEO_CLOSE_NODE(), GEO_END(),
};
''')
# Use BoB's segment slots; replace its contents only on this branch.
(ROOT/'levels/bob/leveldata.c').write_text('''#include <ultra64.h>
#include "sm64.h"
#include "surface_terrains.h"
#include "level_misc_macros.h"
#include "make_const_nonconst.h"
#include "levels/bob/asset_lab/floor.inc.c"
#include "levels/bob/asset_lab/collision.inc.c"
#include "levels/bob/asset_lab/models.inc.c"
/* Shared behavior tables retain references to these stock symbols. */
#include "levels/bob/chain_chomp_gate/collision.inc.c"
#include "levels/bob/seesaw_platform/collision.inc.c"
#include "levels/bob/grate_door/collision.inc.c"
#include "levels/bob/areas/1/trajectory.inc.c"
''')
(ROOT/'levels/bob/geo.c').write_text('''#include <ultra64.h>
#include "sm64.h"
#include "geo_commands.h"
#include "game/level_geo.h"
#include "game/geo_misc.h"
#include "game/camera.h"
#include "make_const_nonconst.h"
#include "levels/bob/asset_lab/header.h"
#include "levels/bob/asset_lab/geo.inc.c"
''')
script='''#include <ultra64.h>
#include "sm64.h"
#include "behavior_data.h"
#include "model_ids.h"
#include "seq_ids.h"
#include "segment_symbols.h"
#include "level_commands.h"
#include "game/level_update.h"
#include "levels/scripts.h"
#include "make_const_nonconst.h"
#include "levels/bob/asset_lab/header.h"
const LevelScript level_bob_entry[] = {
INIT_LEVEL(),
LOAD_YAY0(0x07,_bob_segment_7SegmentRomStart,_bob_segment_7SegmentRomEnd),
ALLOC_LEVEL_POOL(), MARIO(MODEL_MARIO,0x00000001,bhvMario),
'''
for i,name in enumerate(names): script+=f'LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0{i+3},{name}_geo),\n'
script+='AREA(1,lab_area_geo),\n'
for i,name in enumerate(names):
    x=[-600,0,500][i]; y=0 if i==0 else 100
    script+=f'OBJECT(MODEL_LEVEL_GEOMETRY_0{i+3},{x},{y},0,0,0,0,0,bhvStaticObject),\n'
script+='''OBJECT(MODEL_NONE,0,100,850,0,180,0,0x000A0000,bhvSpinAirborneWarp),
WARP_NODE(0x0A,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
WARP_NODE(0xF0,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
WARP_NODE(0xF1,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
TERRAIN(lab_floor_collision), TERRAIN_TYPE(TERRAIN_STONE),
END_AREA(), FREE_LEVEL_POOL(), MARIO_POS(1,180,0,100,850),
CALL(0,lvl_init_or_update), CALL_LOOP(1,lvl_init_or_update),
CLEAR_LEVEL(), SLEEP_BEFORE_EXIT(1), EXIT(),
};
'''
(ROOT/'levels/bob/script.c').write_text(script)
p=ROOT/'include/config/config_debug.h'
p.write_text(p.read_text().replace('// #define TEST_LEVEL LEVEL_BOB','#define TEST_LEVEL LEVEL_BOB'))
p=ROOT/'include/config/config_rom.h'
s=p.read_text()
# HUD identity is independent of cartridge title implementation.
p=ROOT/'src/game/hud.c'
s=p.read_text()
import re
s=re.sub(r'\n        /\* ASSET LAB HUD \*/.*?/\* END ASSET LAB HUD \*/','',s,flags=re.S)
s=s.replace('        create_dl_ortho_matrix();','        create_dl_ortho_matrix();\n        /* ASSET LAB HUD */\n        print_text(40, 200, "ASSET LAB '+str(args.stage)+'");\n        print_text(20, 20, "1 MARKER  2 BLEND  3 GLB");\n        /* END ASSET LAB HUD */')
p.write_text(s)
(ROOT/'build/asset_lab/stage.json').write_text(json.dumps({'stage':args.stage,'assets':names},indent=2)+'\n')
print('Installed Asset Lab stage',args.stage,names)
