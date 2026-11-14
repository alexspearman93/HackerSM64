"""Pinned Fox skeletal clip conversion. No ROM or baked vertex animation."""
from pathlib import Path
import json, struct, hashlib, urllib.request, argparse
parser=argparse.ArgumentParser();parser.add_argument("--asset",choices=["fox","figure"],default="fox");args=parser.parse_args()
import numpy as np
R=Path(__file__).resolve().parents[2]
PIN='4995a638c96dbc94376d3d6164e70fee3ac7f7a2'
SHA='d97044e701822bac5a62696459b27d7b375aada5de8574ed4362edbba94771f7'
name='Fox' if args.asset=='fox' else 'RiggedFigure'
if args.asset=='figure':SHA='d6be85417d3e256861ee733eea6916093a7af7c79c16366181fd8abcaeb38cf5'
out=R/'build/asset_lab'/args.asset;out.mkdir(parents=True,exist_ok=True)
p=out/(name+'.glb')
if not p.exists():p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/{PIN}/Models/{name}/glTF-Binary/{name}.glb').read())
b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==SHA
n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);data=b[28+n:]
def read(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dt={5126:'<f4',5123:'<u2',5121:'u1'}[a['componentType']];size=np.dtype(dt).itemsize*k
 return np.array([np.frombuffer(data,dtype=dt,count=k,offset=v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',size)) for j in range(a['count'])])
def rotation(q):
 q=q/np.linalg.norm(q);x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def sample(times,values,t,quat):
 i=max(0,min(np.searchsorted(times,t,side='right')-1,len(times)-2));u=np.clip((t-times[i])/(times[i+1]-times[i]),0,1);a=values[i].astype(float);b=values[i+1].astype(float)
 if quat:
  a/=np.linalg.norm(a);b/=np.linalg.norm(b);d=a@b
  if d<0:b=-b;d=-d
  if d<.9995:
   theta=np.arccos(np.clip(d,-1,1));return (np.sin((1-u)*theta)*a+np.sin(u*theta)*b)/np.sin(theta)
 v=a*(1-u)+b*u
 return v/np.linalg.norm(v) if quat else v
skin=g['skins'][0];ibm=read(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
primitive=g['meshes'][0]['primitives'][0];assert len(g['meshes'])==1 and len(g['meshes'][0]['primitives'])==1, 'Only one mesh primitive supported'
assert primitive.get('mode',4)==4, 'Only triangles supported'
a=primitive['attributes'];pos=read(a['POSITION']);weights=read(a['WEIGHTS_0']);joints=read(a['JOINTS_0']).astype(int)
assert np.allclose(weights.sum(axis=1),1,atol=1e-5) and joints.max()<len(ibm)
indices=read(primitive['indices']).astype(int).ravel() if 'indices' in primitive else np.arange(len(pos))
pos=pos[indices];weights=weights[indices];joints=joints[indices]
parents={c:i for i,v in enumerate(g['nodes']) for c in v.get('children',[])}
clips={};report=[]
for ai,anim in enumerate(g['animations'][:2]):
 anim=dict(anim);anim.setdefault('name','Animation'+str(ai))
 channels=[]
 for c in anim['channels']:
  s=anim['samplers'][c['sampler']];assert s.get('interpolation','LINEAR')=='LINEAR'
  channels.append((c['target'],read(s['input']).ravel(),read(s['output'])))
 duration=max(t[-1] for _,t,_ in channels);frames=int(np.ceil(duration*30));matrices=[]
 for f in range(frames):
  nodes=[dict(v) for v in g['nodes']]
  for target,t,v in channels:nodes[target['node']][target['path']]=sample(t,v,f/30,target['path']=='rotation')
  cache={}
  def world(i):
   if i in cache:return cache[i]
   v=nodes[i];m=np.eye(4)
   if 'matrix' in v:m=np.array(v['matrix']).reshape(4,4).T
   else:m[:3,:3]=rotation(np.array(v.get('rotation',[0,0,0,1])))*np.array(v.get('scale',[1,1,1]));m[:3,3]=v.get('translation',[0,0,0])
   cache[i]=world(parents[i])@m if i in parents else m
   return cache[i]
  matrices.append([(world(i)@ibm[j])[:3] for j,i in enumerate(skin['joints'])])
 mats=np.array(matrices);assert np.isfinite(mats).all();clips[anim['name']]=mats.astype('float32')
 poses=np.einsum('fvkac,vc,vk->fva',mats[:,joints],np.c_[pos,np.ones(len(pos))],weights)
 assert np.isfinite(poses).all()
 report.append({'name':anim['name'],'frames':frames,'duration':float(duration),'bounds_min':poses.min(axis=(0,1)).tolist(),'bounds_max':poses.max(axis=(0,1)).tolist(),'max_vertex_motion':float(np.max(np.ptp(poses,axis=0)))})
np.savez_compressed(out/'asset.npz',positions=pos,weights=weights,joints=joints,uv=read(a['TEXCOORD_0'])[indices] if 'TEXCOORD_0' in a else np.zeros((len(pos),2)),**clips)
if g.get('images'):
 v=g['bufferViews'][g['images'][0]['bufferView']];(out/'texture.png').write_bytes(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
result={'source_commit':PIN,'source_sha256':SHA,'vertices':len(pos),'triangles':len(pos)//3,'joints':len(ibm),'clips':report,'runtime_verified':False,'notes':'Intermediate joint matrices; no target renderer or ROM integration yet.'}
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
