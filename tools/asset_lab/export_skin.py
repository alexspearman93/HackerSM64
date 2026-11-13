"""Pinned glTF SimpleSkin -> joint matrices + weights, never baked vertex frames.
Strict two-joint fixture adapter; Python/NumPy build-time, C CPU skinning runtime.
"""
from pathlib import Path
import json,struct,hashlib,math,os,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[2];src=Path(os.environ.get('SKIN_PATH',ROOT.parent/'vendor-skin'))
PIN='4995a638c96dbc94376d3d6164e70fee3ac7f7a2'
HASHES={'SimpleSkin.gltf':'8d92e9888340eb98e82a65a1f8b037d9a1d9f09e5fd0b6ba6d40fd93700b3239','SimpleSkin_animation.bin':'ff21b1bc3d0abbe53f7665060ec6c22d873b6e85a7669171a2b6b8ae01c39347','SimpleSkin_geometry.bin':'35f0ca6bc07976c0aadc163d4737758989cfcc9870a99800004c4478fe698b63','SimpleSkin_inverseBindMatrices.bin':'5844ab221cd2ad367420a248f6387b46e5f8498604427730a37ee96b4d4ec599','SimpleSkin_skinningData.bin':'413bc8a8c0da673df767874e6f05f0b00c9261756a08586b9d555bd5535414b5'}
src.mkdir(parents=True,exist_ok=True)
for f,h in HASHES.items():
 p=src/f
 if not p.exists():p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/{PIN}/Models/SimpleSkin/glTF/{f}',timeout=60).read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,f
G=json.loads((src/'SimpleSkin.gltf').read_text())
def read(i):
 a=G['accessors'][i];v=G['bufferViews'][a['bufferView']];data=(src/G['buffers'][v['buffer']]['uri']).read_bytes()
 n={'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt={5123:'H',5126:'f'}[a['componentType']];size=struct.calcsize('<'+fmt*n)
 return np.array([struct.unpack_from('<'+fmt*n,data,v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',size)) for j in range(a['count'])])
prim=G['meshes'][0]['primitives'][0];attrs=prim['attributes'];pos=read(attrs['POSITION']);joints=read(attrs['JOINTS_0']).astype(int);weights=read(attrs['WEIGHTS_0']);indices=read(prim['indices']).astype(int).ravel()
skin=G['skins'][0];ibm=read(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
assert len(pos)==10 and len(indices)==24 and skin['joints']==[1,2]
assert G['nodes'][1].get('children')==[2] and G['nodes'][2]['translation']==[0,1,0]
assert np.allclose(weights.sum(axis=1),1) and np.all(weights>=0) and joints.max()<2
anim=G['animations'][0];assert anim['channels']==[{'sampler':0,'target':{'node':2,'path':'rotation'}}]
samp=anim['samplers'][0];assert samp['interpolation']=='LINEAR'
times=read(samp['input']).ravel();quats=read(samp['output']);assert times[0]==0 and times[-1]==5.5
# This fixture rotates about Z. Independent reference below uses scalar angles.
assert np.allclose(quats[:,:2],0)
angles=np.unwrap(2*np.arctan2(quats[:,2],quats[:,3]));frames=165
mats=[];expected=[]
for f in range(frames):
 t=f/30;ix=min(np.searchsorted(times,t,side='right')-1,len(times)-2);u=(t-times[ix])/(times[ix+1]-times[ix])
 q0=quats[ix]/np.linalg.norm(quats[ix]);q1=quats[ix+1]/np.linalg.norm(quats[ix+1]);dot=float(q0@q1)
 if dot<0:q1=-q1;dot=-dot
 if dot>.9995:q=q0+u*(q1-q0);q/=np.linalg.norm(q)
 else:
  theta=math.acos(np.clip(dot,-1,1));q=(math.sin((1-u)*theta)*q0+math.sin(u*theta)*q1)/math.sin(theta)
 x,y,z,w=q;rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),1],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1]])
 joint=np.array([np.eye(4)@ibm[0],rot@ibm[1]]);mats.append(joint[:,:3,:])
 # Analytic Z-hinge reference, independent of matrix construction and C evaluator.
 angle=float(np.interp(t,times,angles));co,si=math.cos(angle),math.sin(angle);out=[]
 for v,js,ws in zip(pos,joints,weights):
  weight=sum(wt for j,wt in zip(js,ws) if j==1);vx,vy,vz=v;rx=co*vx-si*(vy-1);ry=si*vx+co*(vy-1)+1
  out.append([180*((1-weight)*vx+weight*rx),180*((1-weight)*vy+weight*ry),180*vz])
 expected.append(out)
out=ROOT/'build/asset_lab/skin';out.mkdir(parents=True,exist_ok=True)
def c_array(a):
 a=np.asarray(a)
 if a.ndim==0:return f'{float(a):.9f}f'
 return '{'+','.join(c_array(v) for v in a)+'}'
text='/* CC0 SimpleSkin / Marco Hutter; generated joint matrices, not vertex poses. */\n'
text+='static const float lab_skin_positions[10][3] = '+c_array(pos)+';\n'
text+='static const unsigned char lab_skin_joints[10][4] = '+json.dumps(joints.tolist()).replace('[','{').replace(']','}')+';\n'
text+='static const float lab_skin_weights[10][4] = '+c_array(weights)+';\n'
text+='static const unsigned char lab_skin_indices[24] = {'+','.join(map(str,indices))+'};\n'
text+='static const float lab_skin_matrices[165][2][3][4] = '+c_array(np.array(mats))+';\n'
(out/'skin_data.h').write_text(text)
(out/'expected.json').write_text(json.dumps(expected))
report={'source_commit':PIN,'source_hashes':HASHES,'vertices':10,'triangles':8,'joints':2,'influences_max':2,'fps':30,'frames':165,'duration':5.5,'scale':180,'backend':'CPU linear blend skinning from joint matrices / inverse binds / source weights','runtime_vertex_pose_baking':False,'matrix_bytes':165*2*3*4*4,'limitations':['two-joint fixture adapter','unlit weight visualization','no collision or rig retargeting','not native SM64 joint-animation format']}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
