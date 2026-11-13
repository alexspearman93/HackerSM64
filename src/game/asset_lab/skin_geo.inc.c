#include "game/game_init.h"
#include "skin_math.h"
/* Read-only emulator diagnostics expose the actual pose submitted for rendering. */
s32 gLabSkinFrame;
f32 gLabSkinProbe[10][3];
Gfx *geo_lab_skin(s32 callContext, struct GraphNode *node, UNUSED Mat4 mtx) {
    struct GraphNodeGenerated *gen=(struct GraphNodeGenerated *)node;
    Gfx *dl,*p; Vtx *vertices; float pose[10][3]; int i,frame;
    if(callContext!=GEO_CONTEXT_RENDER) return NULL;
    vertices=alloc_display_list(10*sizeof(Vtx));
    dl=alloc_display_list(20*sizeof(Gfx));
    if(!vertices || !dl) return NULL;
    SET_GRAPH_NODE_LAYER(gen->fnNode.node.flags,LAYER_OPAQUE);
    frame=gen->parameter ? gGlobalTimer%165 : 0;
    lab_skin_evaluate(frame,pose);
    if(gen->parameter) {gLabSkinFrame=frame; for(i=0;i<10;i++) vec3f_copy(gLabSkinProbe[i],pose[i]);}
    for(i=0;i<10;i++) {
        float w=lab_skin_weights[i][1];
        make_vertex(vertices,i,(s16)pose[i][0],(s16)pose[i][1],(s16)pose[i][2],0,0,
            (u8)(40+215*w),(u8)(170-50*w),(u8)(240-210*w),255);
    }
    p=dl;
    gDPPipeSync(p++);
    gSPClearGeometryMode(p++,G_LIGHTING|G_CULL_BOTH);
    gDPSetCombineMode(p++,G_CC_SHADE,G_CC_SHADE);
    gSPTexture(p++,0,0,0,G_TX_RENDERTILE,G_OFF);
    gSPVertex(p++,vertices,10,0);
    for(i=0;i<24;i+=6) gSP2Triangles(p++,lab_skin_indices[i],lab_skin_indices[i+1],lab_skin_indices[i+2],0,lab_skin_indices[i+3],lab_skin_indices[i+4],lab_skin_indices[i+5],0);
    gDPPipeSync(p++);
    gSPSetGeometryMode(p++,G_LIGHTING|G_CULL_BACK);
    gSPEndDisplayList(p++);
    return dl;
}
