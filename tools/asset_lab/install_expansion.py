"""Install existing Kenney props, matching ramp collision and rigid glTF animation."""
from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[2]
subprocess.run(['python3',str(R/'tools/asset_lab/install_scene.py'),'--stage','4'],check=True)
d=R/'levels/bob/asset_lab';e=R/'build/asset_lab/export'
for n in ['tree','ramp','animated']:
 name='lab_'+n;shutil.copytree(e/name,d/name,dirs_exist_ok=True)
 with (d/'header.h').open('a') as f:f.write((d/name/'header.h').read_text()+f'\nextern const GeoLayout {name}_geo[];\n')
 with (d/'models.inc.c').open('a') as f:f.write(f'#include "levels/bob/asset_lab/{name}/model.inc.c"\n')
 with (d/'geo.inc.c').open('a') as f:f.write(f'const GeoLayout {name}_geo[] = {{ GEO_NODE_START(), GEO_OPEN_NODE(), GEO_DISPLAY_LIST(LAYER_OPAQUE,{name}_{name}_mesh), GEO_CLOSE_NODE(), GEO_END(), }};\n')
with (d/'collision.inc.c').open('a') as f:f.write((e/'ramp_collision.inc.c').read_text())
with (d/'header.h').open('a') as f:f.write('extern const Collision lab_ramp_collision[];\n')
shutil.copy(e/'animation.inc.c',d/'animation.inc.c')
p=R/'levels/bob/script.c';s=p.read_text().replace('extern const BehaviorScript bhvLabCrate[];','extern const BehaviorScript bhvLabCrate[], bhvLabRamp[], bhvLabAnimated[];')
s=s.replace('AREA(1,lab_area_geo),','''LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_07,lab_tree_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_08,lab_ramp_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_09,lab_animated_geo),
AREA(1,lab_area_geo),
OBJECT(MODEL_LEVEL_GEOMETRY_07,-750,0,-650,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_08,650,0,-650,0,0,0,0,bhvLabRamp),
OBJECT(MODEL_LEVEL_GEOMETRY_09,-100,300,-650,0,0,0,0,bhvLabAnimated),''');p.write_text(s)
p=R/'include/config/config_debug.h';p.write_text(p.read_text()+'\n#define ASSET_LAB_EXPANSION\n')
p=R/'src/game/hud.c';p.write_text(p.read_text().replace('print_text(40, 200, "ASSET LAB 4")','print_text(12, 215, "LAB 108")'))
