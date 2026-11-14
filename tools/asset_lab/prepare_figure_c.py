from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[2];d=np.load(R/'build/asset_lab/figure/asset.npz')
def arr(a):
 a=np.asarray(a)
 if a.ndim==0:return str(int(a)) if a.dtype.kind in 'iu' else f'{float(a):.7f}f'
 return '{'+','.join(arr(x) for x in a)+'}'
s='/* RiggedFigure: Cesium, CC-BY-4.0; adapted for N64. */\n'
for name in ['positions','weights','joints','uv','Animation0']:
 a=d[name];s+='static const '+('unsigned char' if name=='joints' else 'float')+' figure_'+name+''.join('['+str(x)+']' for x in a.shape)+'='+arr(a)+';\n'
(R/'src/game/asset_lab/figure_data.h').write_text(s)
