Vtx lab_marker_lab_marker_mesh_vtx_cull[8] = {
	{{ {0, 0, -100}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {0, 0, 0}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {0, 150, 0}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {0, 150, -100}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {200, 0, -100}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {200, 0, 0}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {200, 150, 0}, 0, {0, 0}, {0, 0, 0, 0} }},
	{{ {200, 150, -100}, 0, {0, 0}, {0, 0, 0, 0} }},
};

Vtx lab_marker_lab_marker_mesh_vtx_0[17] = {
	{{ {0, 0, 0}, 0, {-16, 1008}, {0, 21, 125, 255} }},
	{{ {200, 0, 0}, 0, {1008, 1008}, {0, 21, 125, 255} }},
	{{ {35, 150, -25}, 0, {1008, -16}, {0, 21, 125, 255} }},
	{{ {200, 0, 0}, 0, {-16, 1008}, {85, 94, 0, 255} }},
	{{ {200, 0, -100}, 0, {1008, 1008}, {85, 94, 0, 255} }},
	{{ {35, 150, -25}, 0, {1008, -16}, {85, 94, 0, 255} }},
	{{ {200, 0, -100}, 0, {-16, 1008}, {0, 57, 142, 255} }},
	{{ {0, 0, -100}, 0, {1008, 1008}, {0, 57, 142, 255} }},
	{{ {35, 150, -25}, 0, {1008, -16}, {0, 57, 142, 255} }},
	{{ {0, 0, -100}, 0, {-16, 1008}, {132, 29, 0, 255} }},
	{{ {0, 0, 0}, 0, {1008, 1008}, {132, 29, 0, 255} }},
	{{ {35, 150, -25}, 0, {1008, -16}, {132, 29, 0, 255} }},
	{{ {0, 0, 0}, 0, {-16, 1008}, {0, 129, 0, 255} }},
	{{ {0, 0, -100}, 0, {1008, 1008}, {0, 129, 0, 255} }},
	{{ {200, 0, -100}, 0, {1008, -16}, {0, 129, 0, 255} }},
	{{ {200, 0, -100}, 0, {1008, 1008}, {0, 129, 0, 255} }},
	{{ {200, 0, 0}, 0, {1008, -16}, {0, 129, 0, 255} }},
};

Gfx lab_marker_lab_marker_mesh_tri_0[] = {
	gsSPVertex(lab_marker_lab_marker_mesh_vtx_0 + 0, 17, 0),
	gsSP2Triangles(0, 1, 2, 0, 3, 4, 5, 0),
	gsSP2Triangles(6, 7, 8, 0, 9, 10, 11, 0),
	gsSP2Triangles(12, 13, 14, 0, 12, 15, 16, 0),
	gsSPEndDisplayList(),
};

Gfx mat_lab_marker_lab_marker_material[] = {
	gsDPPipeSync(),
	gsDPSetCombineLERP(PRIMITIVE, 0, SHADE, 0, 0, 0, 0, ENVIRONMENT, PRIMITIVE, 0, SHADE, 0, 0, 0, 0, ENVIRONMENT),
	gsDPSetAlphaDither(G_AD_NOISE),
	gsSPTexture(65535, 65535, 0, 0, 1),
	gsDPSetPrimColor(0, 0, 255, 255, 255, 255),
	gsSPEndDisplayList(),
};

Gfx mat_revert_lab_marker_lab_marker_material[] = {
	gsDPPipeSync(),
	gsDPSetAlphaDither(G_AD_DISABLE),
	gsSPEndDisplayList(),
};

Gfx lab_marker_lab_marker_mesh[] = {
	gsSPClearGeometryMode(G_LIGHTING),
	gsSPVertex(lab_marker_lab_marker_mesh_vtx_cull + 0, 8, 0),
	gsSPSetGeometryMode(G_LIGHTING),
	gsSPCullDisplayList(0, 7),
	gsSPDisplayList(mat_lab_marker_lab_marker_material),
	gsSPDisplayList(lab_marker_lab_marker_mesh_tri_0),
	gsSPDisplayList(mat_revert_lab_marker_lab_marker_material),
	gsDPPipeSync(),
	gsSPSetGeometryMode(G_LIGHTING),
	gsSPClearGeometryMode(G_TEXTURE_GEN),
	gsDPSetCombineLERP(0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT, 0, 0, 0, SHADE, 0, 0, 0, ENVIRONMENT),
	gsSPTexture(65535, 65535, 0, 0, 0),
	gsSPEndDisplayList(),
};

