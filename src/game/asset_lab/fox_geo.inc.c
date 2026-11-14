#include "fox_data.h"
/* Frame-owned vertices, 30 at a time: compatible with target vertex cache. */
Gfx *geo_lab_fox(s32 context, struct GraphNode *node, UNUSED Mat4 mtx) {
 struct GraphNodeGenerated *gen=(struct GraphNodeGenerated *)node;
 Gfx *dl,*p; Vtx *v; int i,a,k,j,b,n,t,walk,frame; float x[3],q,offset,sign;
 const float (*mat)[3][4];
 if(context!=GEO_CONTEXT_RENDER)return NULL;
 t=gGlobalTimer%720;sign=t<360?1:-1;t%=360;walk=(t>=90&&t<270);frame=walk?(t-90)%22:t%103;
 mat=walk?fox_Walk[frame]:fox_Survey[frame];
 offset=t<90?-240:(t<270?-240+(t-90)*480.0f/180:240);
 offset*=sign;
 v=alloc_display_list(1728*sizeof(Vtx));dl=alloc_display_list(750*sizeof(Gfx));if(!v||!dl)return NULL;
 for(i=0;i<1728;i++){
  for(a=0;a<3;a++){x[a]=0;for(k=0;k<4;k++){j=fox_joints[i][k];q=mat[j][a][3];for(b=0;b<3;b++)q+=mat[j][a][b]*fox_positions[i][b];x[a]+=q*fox_weights[i][k];}}
  make_vertex(v,i,(s16)(sign*x[2]*2+offset),(s16)(x[1]*2+4),(s16)(-sign*x[0]*2),fox_uv[i][0]*1024,fox_uv[i][1]*1024,255,255,255,255);
 }
 SET_GRAPH_NODE_LAYER(gen->fnNode.node.flags,LAYER_OPAQUE);p=dl;
 gDPPipeSync(p++);gSPClearGeometryMode(p++,G_LIGHTING|G_CULL_BOTH);gDPSetCombineMode(p++,G_CC_DECALRGBA,G_CC_DECALRGBA);
 gSPTexture(p++,65535,65535,0,G_TX_RENDERTILE,G_ON);
 gDPLoadTextureBlock(p++,fox_texture,G_IM_FMT_RGBA,G_IM_SIZ_16b,32,32,0,G_TX_WRAP,G_TX_WRAP,5,5,G_TX_NOLOD,G_TX_NOLOD);
 for(i=0;i<1728;i+=30){n=1728-i;if(n>30)n=30;gSPVertex(p++,v+i,n,0);for(j=0;j<n;j+=3)gSP1Triangle(p++,j,j+1,j+2,0);}
 gDPPipeSync(p++);gSPTexture(p++,0,0,0,G_TX_RENDERTILE,G_OFF);gSPSetGeometryMode(p++,G_LIGHTING|G_CULL_BACK);gDPSetCombineMode(p++,G_CC_SHADE,G_CC_SHADE);gSPEndDisplayList(p++);return dl;
}
