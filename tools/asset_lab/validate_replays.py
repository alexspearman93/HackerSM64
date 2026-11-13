"""Validate observations from real controller replays; never drives/writes game memory."""
import argparse,csv,json
p=argparse.ArgumentParser();p.add_argument('evidence');a=p.parse_args()
from pathlib import Path
root=Path(a.evidence)
def rows(name): return [{k:float(v) if k!='action' else v for k,v in r.items()} for r in csv.DictReader((root/(name+'-trace.csv')).open())]
s=rows('solid');b=rows('punch');g=rows('ground_pound')
assert all(abs(r['z']-150)<0.1 and abs(r['y'])<0.1 for r in s if 170<=r['poll']<=200)
assert all(abs(r['y']-200)<0.1 and abs(r['floor']-200)<0.1 for r in s if 260<=r['poll']<=280)
assert any(r['coins']==1 for r in b) and max(r['coins'] for r in b)==1
assert any(r['z']<0 and abs(r['y'])<0.1 for r in b if r['poll']>260)
assert any(r['action']=='008008a9' for r in g) # ACT_GROUND_POUND, this target revision
assert any(abs(r['floor']-200)<0.1 for r in g if 260<=r['poll']<=280)
assert all(abs(r['floor'])<0.1 and abs(r['y'])<0.1 for r in g if 320<=r['poll']<=330)
for data in (s,b,g): assert max(r['poll'] for r in data)>=350
report={'solid_wall':True,'stand_on_top':True,'punch_coin_collected':True,'removed_collision':True,'ground_pound_removes_platform':True,'iphone_accepted':False,'audio_listened':False}
(root/'lab105-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
