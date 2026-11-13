from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[2]
subprocess.run(['python3',str(R/'tools/asset_lab/install_expansion.py')],check=True)
shutil.copy(R/'build/asset_lab/skin/skin_data.h',R/'src/game/asset_lab/skin_data.h')
p=R/'include/config/config_debug.h';p.write_text(p.read_text()+'\n#define ASSET_LAB_SKIN\n')
p=R/'levels/bob/asset_lab/header.h';p.write_text(p.read_text()+'\nextern const GeoLayout lab_skin_bind_geo[],lab_skin_animated_geo[];\n')
p=R/'levels/bob/asset_lab/geo.inc.c';p.write_text(p.read_text()+'''\nGfx *geo_lab_skin(s32 callContext, struct GraphNode *node, Mat4 mtx);
const GeoLayout lab_skin_bind_geo[] = { GEO_NODE_START(),GEO_OPEN_NODE(),GEO_ASM(0,geo_lab_skin),GEO_CLOSE_NODE(),GEO_END(), };
const GeoLayout lab_skin_animated_geo[] = { GEO_NODE_START(),GEO_OPEN_NODE(),GEO_ASM(1,geo_lab_skin),GEO_CLOSE_NODE(),GEO_END(), };
''')
p=R/'levels/bob/script.c';s=p.read_text().replace('AREA(1,lab_area_geo),','''LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0A,lab_skin_bind_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0B,lab_skin_animated_geo),
AREA(1,lab_area_geo),
OBJECT(MODEL_LEVEL_GEOMETRY_0A,-250,0,350,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_0B,250,0,350,0,0,0,0,bhvStaticObject),''');p.write_text(s)
p=R/'src/game/hud.c';p.write_text(p.read_text().replace('"LAB 108"','"LAB 109"').replace('"1 DISPLAY 2 SOLID 3 BREAK"','"BIND POSE     SKINNED"'))
