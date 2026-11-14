#include "figure_data.h"
/* Frame-owned vertices, 30 at a time: compatible with target vertex cache. */
Gfx *geo_lab_figure(s32 context, struct GraphNode *node, UNUSED Mat4 mtx) {
 struct GraphNodeGenerated *gen=(struct GraphNodeGenerated *)node;
 Gfx *dl,*p; Vtx *v; int i,a,k,j,b,n,t,walk,frame; float x[3],q,offset,sign;
 const float (*mat)[3][4];
 if(context!=GEO_CONTEXT_RENDER)return NULL;
 mat=figure_Animation0[gGlobalTimer%38];
 v=alloc_display_list(768*sizeof(Vtx));dl=alloc_display_list(350*sizeof(Gfx));if(!v||!dl)return NULL;
 for(i=0;i<768;i++){
  for(a=0;a<3;a++){x[a]=0;for(k=0;k<4;k++){j=figure_joints[i][k];q=mat[j][a][3];for(b=0;b<3;b++)q+=mat[j][a][b]*figure_positions[i][b];x[a]+=q*figure_weights[i][k];}}
  make_vertex(v,i,(s16)(x[0]*160),(s16)(x[1]*160),(s16)(x[2]*160),figure_uv[i][0]*1024,figure_uv[i][1]*1024,170,190,220,255);
 }
 SET_GRAPH_NODE_LAYER(gen->fnNode.node.flags,LAYER_OPAQUE);p=dl;
 gDPPipeSync(p++);gSPClearGeometryMode(p++,G_LIGHTING|G_CULL_BOTH);gDPSetCombineMode(p++,G_CC_SHADE,G_CC_SHADE);
 gSPTexture(p++,65535,65535,0,G_TX_RENDERTILE,G_OFF);
 for(i=0;i<768;i+=30){n=768-i;if(n>30)n=30;gSPVertex(p++,v+i,n,0);for(j=0;j<n;j+=3)gSP1Triangle(p++,j,j+1,j+2,0);}
 gDPPipeSync(p++);gSPTexture(p++,0,0,0,G_TX_RENDERTILE,G_OFF);gSPSetGeometryMode(p++,G_LIGHTING|G_CULL_BACK);gDPSetCombineMode(p++,G_CC_SHADE,G_CC_SHADE);gSPEndDisplayList(p++);return dl;
}
