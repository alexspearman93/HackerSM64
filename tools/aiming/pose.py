"""Set arm forward (-Z in Mario model coordinates), retaining glove orientation."""
from pathlib import Path
import re,json,numpy as np
from scipy.spatial.transform import Rotation as R
p=Path(__file__).resolve().parents[2]
f=json.loads((p/'tools/pistol-alignment/idle_c5_frames.json').read_text())['frames'][0]
parents=[-1,0,1,2,2,4,5,6,2,8,9,10];m=[]
for i,a in enumerate(f[:12]):
 r=R.from_euler('xyz',np.array(a)*360/65536,degrees=True).as_matrix();m.append(r if parents[i]<0 else m[parents[i]]@r)
gun=R.from_euler('YXZ',[112,11,-116],degrees=True).as_matrix()
forward=m[11]@gun[:,2];up=m[11]@gun[:,1]
t=np.column_stack((forward,up,np.cross(forward,up)))
angle=lambda r:np.rint(R.from_matrix(r).as_euler('xyz')*65536/(2*np.pi)).astype(int).tolist()
pose={8:f[8],9:angle(m[8].T@t),10:[0,0,0],11:angle(t.T@m[11])}
for name in ['48','72_73','C3','C4','C5']:
 file=p/f'assets/anims/anim_{name}.inc.c';s=file.read_text()
 im=re.search(r'anim_'+name+r'_indices\[\] = \{(.*?)\n\};',s,re.S);ix=[int(x,16) for x in re.findall(r'0x[\da-fA-F]+',im[1])]
 vm=re.search(r'anim_'+name+r'_values\[\] = \{(.*?)\n\};',s,re.S);vs=[int(x,16) for x in re.findall(r'0x[\da-fA-F]+',vm[1])]
 for j,a in pose.items():
  for axis,v in enumerate(a):
   k=6+(j*3+axis)*2;assert ix[k]==1;vs[ix[k+1]]=v&65535
 body='\n'+''.join('    '+', '.join(f'0x{x:04X}' for x in vs[i:i+8])+',\n' for i in range(0,len(vs),8))
 file.write_text(s[:vm.start(1)]+body+s[vm.end(1):])
print(pose)
