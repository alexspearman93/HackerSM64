#!/usr/bin/env python3
"""ROM-free SM64 idle skeleton parity checks. Standard library only.
C reference: src/engine/math_util.c mtxf_rotate_xyz_and_translate_and_mul.
Independent target: ZYX Euler composed as Rz @ Ry @ Rx (Three.js convention).
This tests joint transforms, not emulator rendering, geometry, or GPU rounding.
"""
import math, re, pathlib, unittest
BASE=pathlib.Path(__file__).resolve().parents[2]
def parse(name):
    source=(BASE/'assets/anims/anim_C5.inc.c').read_text()
    body=re.search(r'\\b'+name+r'\\[\\]\\s*=\\s*\\{(.*?)\\};',source,re.S).group(1)
    return [int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|-?\\d+',body)]
def data():
    v=[n-65536 if n>=32768 else n for n in parse('anim_C5_values')]
    ix=parse('anim_C5_indices')
    source=(BASE/'tools/pistol-alignment/skeleton.generated.c').read_text()
    parents=list(map(int,re.findall(r'-?\\d+',re.search(r'gSkelParent\\[20\\] = \\{(.*?)\\}',source,re.S).group(1))))
    offsets=[tuple(map(int,x)) for x in re.findall(r'\\{\\s*(-?\\d+),\\s*(-?\\d+),\\s*(-?\\d+)\\s*\\}',source.split('gSkelOffset')[1])]
    assert len(parents)==len(offsets)==20 and len(ix)==126
    def channel(frame,ch):
        count,start=ix[2*ch:2*ch+2]
        assert count>0
        return v[start+min(frame,count-1)]
    return parents,offsets,channel
def mul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def identity():
    return [[float(i==j) for j in range(4)] for i in range(4)]
def reference(angles,offset):
    x,y,z=[v*math.pi/32768 for v in angles]
    sx,cx=math.sin(x),math.cos(x);sy,cy=math.sin(y),math.cos(y);sz,cz=math.sin(z),math.cos(z)
    m=identity()
    m[0][:3]=[cy*cz,sx*cz*sy-cx*sz,cx*cz*sy+sx*sz]
    m[1][:3]=[cy*sz,sx*sz*sy+cx*cz,cx*sz*sy-sx*cz]
    m[2][:3]=[-sy,sx*cy,cx*cy]
    for i in range(3):m[i][3]=offset[i]
    return m
def target(angles,offset):
    x,y,z=[v*math.pi/32768 for v in angles]
    sx,cx=math.sin(x),math.cos(x);sy,cy=math.sin(y),math.cos(y);sz,cz=math.sin(z),math.cos(z)
    rx=identity();rx[1][1]=cx;rx[1][2]=-sx;rx[2][1]=sx;rx[2][2]=cx
    ry=identity();ry[0][0]=cy;ry[0][2]=sy;ry[2][0]=-sy;ry[2][2]=cy
    rz=identity();rz[0][0]=cz;rz[0][1]=-sz;rz[1][0]=sz;rz[1][1]=cz
    m=mul(mul(rz,ry),rx)
    for i in range(3):m[i][3]=offset[i]
    return m
class TestMarioMatrices(unittest.TestCase):
    def test_all_idle_frames_and_joints(self):
        parents,offsets,channel=data()
        worst=0.0;compared=0
        for frame in range(30):
            refworld=[];targetworld=[]
            for joint in range(20):
                angles=[channel(frame,3+joint*3+axis) for axis in range(3)]
                xyz=list(offsets[joint])
                if joint==0: # C5 flags=1 (NOLOOP); root translation enabled; animYTransDivisor=189
                    xyz=[xyz[k]+channel(frame,k) for k in range(3)]
                parent=parents[joint]
                a=reference(angles,xyz);b=target(angles,xyz)
                if parent>=0:
                    a=mul(refworld[parent],a);b=mul(targetworld[parent],b)
                refworld.append(a);targetworld.append(b)
                worst=max(worst,max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)))
                compared+=1
        print(f'Compared {compared} joint-frame world matrices; max element delta {worst:.3e}')
        self.assertEqual(compared,600)
        self.assertLess(worst,1e-8)
    def test_rotation_order_is_not_xyz_three_euler(self):
        a=reference([6000,12000,-9000],[10,20,30])
        b=target([6000,12000,-9000],[10,20,30])
        self.assertLess(max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)),1e-12)
    def test_animation_root_translation(self):
        _,_,channel=data()
        self.assertEqual([channel(0,i) for i in range(3)],[0,171,-1])
        self.assertEqual([channel(29,i) for i in range(3)],[0,171,-1])
if __name__=='__main__':unittest.main(verbosity=2)
