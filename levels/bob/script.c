#include <ultra64.h>
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
extern const BehaviorScript bhvLabCrate[], bhvLabRamp[], bhvLabAnimated[];
const LevelScript level_bob_entry[] = {
INIT_LEVEL(),
LOAD_YAY0(0x07,_bob_segment_7SegmentRomStart,_bob_segment_7SegmentRomEnd),
ALLOC_LEVEL_POOL(), MARIO(MODEL_MARIO,0x00000001,bhvMario),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_06,lab_crate_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_03,lab_marker_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_04,lab_blend_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_05,lab_glb_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_07,lab_tree_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_08,lab_ramp_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_09,lab_animated_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0A,lab_skin_bind_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0B,lab_skin_animated_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0C,lab_fox_geo),
LOAD_MODEL_FROM_GEO(MODEL_LEVEL_GEOMETRY_0D,lab_figure_geo),
AREA(1,lab_area_geo),
OBJECT(MODEL_LEVEL_GEOMETRY_0D,-550,0,650,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_0C,0,0,650,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_0A,-250,0,350,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_0B,250,0,350,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_07,-750,0,-650,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_08,650,0,-650,0,0,0,0,bhvLabRamp),
OBJECT(MODEL_LEVEL_GEOMETRY_09,-100,300,-650,0,0,0,0,bhvLabAnimated),
OBJECT(MODEL_LEVEL_GEOMETRY_06,-500,0,0,0,0,0,0,bhvStaticObject),
OBJECT(MODEL_LEVEL_GEOMETRY_06,0,0,0,0,0,0,0,bhvLabCrate),
OBJECT(MODEL_LEVEL_GEOMETRY_06,500,0,0,0,0,0,0x00010000,bhvLabCrate),
OBJECT(MODEL_NONE,0,100,850,0,180,0,0x000A0000,bhvSpinAirborneWarp),
WARP_NODE(0x0A,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
WARP_NODE(0xF0,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
WARP_NODE(0xF1,LEVEL_BOB,1,0x0A,WARP_NO_CHECKPOINT),
TERRAIN(lab_floor_collision), TERRAIN_TYPE(TERRAIN_STONE),
END_AREA(), FREE_LEVEL_POOL(), MARIO_POS(1,180,0,100,850),
CALL(0,lvl_init_or_update), CALL_LOOP(1,lvl_init_or_update),
CLEAR_LEVEL(), SLEEP_BEFORE_EXIT(1), EXIT(),
};
