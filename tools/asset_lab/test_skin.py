"""Compare actual C skinning against independent analytic source-animation poses."""
from pathlib import Path
import subprocess,tempfile,ctypes,json,numpy as np
R=Path(__file__).resolve().parents[2];expected=np.array(json.loads((R/'build/asset_lab/skin/expected.json').read_text()))
assert (R/'src/game/asset_lab/skin_data.h').read_bytes()==(R/'build/asset_lab/skin/skin_data.h').read_bytes(), 'Committed joint data differs from fresh conversion'
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'test.c').write_text('#include "skin_math.h"\nvoid evaluate(int frame,float *out){lab_skin_evaluate(frame,(float(*)[3])out);}\n')
 subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(R/'src/game/asset_lab'),str(p/'test.c'),'-o',str(p/'test.so')],check=True)
 lib=ctypes.CDLL(str(p/'test.so'));lib.evaluate.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_float)]
 poses=[]
 for frame in range(165):
  out=(ctypes.c_float*30)();lib.evaluate(frame,out);poses.append(np.array(out).reshape(10,3))
 poses=np.array(poses);err=float(np.max(np.abs(poses-expected)));assert err<0.001,err
 assert np.allclose(poses[:,0,:],expected[0,0,:],atol=.001) # anchored base
 assert np.ptp(poses[:,8,0])>300 # bending top, no whole-object rigid motion
 report={'frames_checked':165,'vertices_per_frame':10,'max_c_float_error':err,'anchor_fixed':True,'tip_moves':True,'independent_reference':'source scalar Z-hinge interpolation','runtime':'C linear blend skinning'}
 (R/'build/asset_lab/skin/math-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
