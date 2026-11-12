"""Original deterministic arcade shot: bright crack, low thump, short noise tail."""
from pathlib import Path
import numpy as np
import struct
rate=22050
t=np.arange(int(rate*.18))/rate
rng=np.random.default_rng(6411)
n=rng.standard_normal(len(t))
high=n-np.convolve(n,np.ones(7)/7,mode='same')
phase=2*np.pi*(70*t+85*.018*(1-np.exp(-t/.018)))
y=.70*np.sin(phase)*np.exp(-t/.047)+.38*high*np.exp(-t/.012)+.20*n*np.exp(-t/.035)
y*=np.minimum(t/.0004,1)*np.minimum((.18-t)/.014,1)
y=np.tanh(y*1.5);y*=.87/max(abs(y))
p=Path(__file__).resolve().parents[2]/'sound/samples/sfx_5/zz_custom_pistol.aiff'
pcm=(y*32767).astype('>i2').tobytes()
comm=struct.pack('>hIh',1,len(y),16)+bytes.fromhex('400dac44000000000000')
ssnd=bytes(8)+pcm
body=b'AIFF'+b'COMM'+struct.pack('>I',len(comm))+comm+b'SSND'+struct.pack('>I',len(ssnd))+ssnd
p.write_bytes(b'FORM'+struct.pack('>I',len(body))+body)
print(p)
