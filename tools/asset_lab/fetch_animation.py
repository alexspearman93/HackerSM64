"""Download only the pinned CC0 glTF sample dependencies; no game data."""
import urllib.request,hashlib,os
from pathlib import Path
p=Path(os.environ.get('ANIMATED_PATH',Path(__file__).resolve().parents[3]/'vendor-animated'));p.mkdir(parents=True,exist_ok=True)
base='https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/4995a638c96dbc94376d3d6164e70fee3ac7f7a2/Models/AnimatedCube/glTF/'
for f,h in {'AnimatedCube.gltf':'59a3c451a5167b8ac4b59d61d4b94b2b7a215ee827efaed75629677a1217b552','AnimatedCube.bin':'82de770fc82b48a77a33bb26abd4d7e75620491b36ddf98e8dca69fa73dd798c','AnimatedCube_BaseColor.png':'0750d5a03c1bebc640571e309f66c6e88efbff2ef4c120619466a7014551bb9a'}.items():
 data=urllib.request.urlopen(base+f,timeout=60).read();assert hashlib.sha256(data).hexdigest()==h
 (p/f).write_bytes(data)
print('Pinned animation inputs verified')
