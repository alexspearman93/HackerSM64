"""Validate read-only emulator skin telemetry against independent source poses."""
import argparse, json
from pathlib import Path
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('trace', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
expected = np.array(json.loads((root/'build/asset_lab/skin/expected.json').read_text()))
rows = np.loadtxt(a.trace, delimiter=',')
poses = rows[:, 2:].reshape(-1, 10, 3)
valid = np.any(poses != 0, axis=(1, 2))  # startup before first rendered pose
frames = rows[valid, 1].astype(int)
poses = poses[valid]
assert set(frames) == set(range(165)), 'Incomplete animation coverage'
error = float(np.max(np.abs(poses - expected[frames])))
assert error < .001, error
assert np.allclose(poses[:, :2], expected[0, :2], atol=.001)
report = {'samples':len(frames), 'unique_frames':len(set(frames)),
          'max_error_game_units':error, 'base_anchored':True,
          'source':'read-only final-ROM render-pose telemetry',
          'vertex_integer_quantization':'rendered Vtx coordinates truncate toward zero (<1 unit)'}
a.output.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
