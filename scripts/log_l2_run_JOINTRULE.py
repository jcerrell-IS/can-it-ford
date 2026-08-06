import argparse
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_CSV = os.path.join(REPO, 'data', 'scenario_sweep.csv')
ORG = 'jcerrell29-claremont-mckenna-college'

JOINT_DEPTH_CAP = 0.30
JOINT_VEL_CAP = 3.0
JOINT_PRODUCT_CAP = 0.30

PROVENANCE_FIELDS = [
    'n_grid', 'dx', 'water_layers', 'solid_volume', 'realized_rho',
    'water_eta', 'floor_friction', 'vehicle_asset', 'vehicle_mass_kg',
]

ap = argparse.ArgumentParser()
ap.add_argument('depth', type=float)
ap.add_argument('velocity', type=float)
ap.add_argument('l2', choices=['FORD', 'NO-FORD'])
ap.add_argument('--push', action='store_true',
                help='actually write to wandb.ai; without this flag nothing leaves this machine')
ap.add_argument('--n-grid', type=int, default=None)
ap.add_argument('--dx', type=float, default=None)
ap.add_argument('--water-layers', type=int, default=None)
ap.add_argument('--solid-volume', type=float, default=None)
ap.add_argument('--realized-rho', type=float, default=None)
ap.add_argument('--water-eta', type=float, default=None)
ap.add_argument('--floor-friction', type=float, default=None)
ap.add_argument('--vehicle-asset', default=None)
ap.add_argument('--vehicle-mass-kg', type=float, default=None)
args = ap.parse_args()

depth = args.depth
velocity = args.velocity
l2 = args.l2


def joint_rule(d, v):
    if d <= JOINT_DEPTH_CAP and v <= JOINT_VEL_CAP and round(d * v, 6) <= JOINT_PRODUCT_CAP:
        return 'FORD'
    return 'NO-FORD'


with open(SWEEP_CSV, newline='', encoding='utf-8-sig') as fh:
    sweep_rows = list(csv.DictReader(fh))

sweep_table = {}
for r in sweep_rows:
    sweep_table[(round(float(r['depth_m']), 6), round(float(r['velocity_ms']), 6))] = r['L1_verdict']

key = (round(depth, 6), round(velocity, 6))
if key in sweep_table:
    l1 = sweep_table[key]
    l1_source = 'data/scenario_sweep.csv column L1_verdict'
else:
    l1 = joint_rule(depth, velocity)
    l1_source = 'joint rule applied directly, (depth, velocity) not in the sweep grid'

haz = round(depth * velocity, 3)
L1_RULE = 'joint: depth <= 0.30 m AND velocity <= 3.0 m/s AND D*V <= 0.30 m2/s'

provenance = {f: getattr(args, f) for f in PROVENANCE_FIELDS}
missing = [f for f, v in provenance.items() if v is None]

print(f'd={depth} m, v={velocity} m/s')
print(f'  L1       {l1}')
print(f'  L1 rule  {L1_RULE}')
print(f'  L1 source{"":1s} {l1_source}')
print(f'  D*V      {haz} m2/s')
print(f'  L2       {l2}')
print(f'  diverge  {l1 != l2}')
if missing:
    print(f'  PROVENANCE INCOMPLETE, {len(missing)} unset: {", ".join(missing)}')

if not args.push:
    print()
    print('DRY RUN. Nothing was sent to wandb.ai. Re-run with --push to write.')
    sys.exit(0)

import wandb

wandb.init(
    project='can-it-ford',
    entity=ORG,
    name=f'L2_d{depth}_v{velocity}',
    tags=['L2', 'Warp-MPM', 'Vista'],
    config={
        'depth_m': depth,
        'velocity_ms': velocity,
        'L1_rule': L1_RULE,
        'L1_source': l1_source,
        'l1_depth_cap_m': JOINT_DEPTH_CAP,
        'l1_velocity_cap_ms': JOINT_VEL_CAP,
        'l1_product_cap_m2s': JOINT_PRODUCT_CAP,
        'level': 'L2',
        'compute': 'Vista_GH200',
        **provenance,
    },
)

wandb.log({
    'depth_m': depth,
    'velocity_ms': velocity,
    'dv_product': round(depth * velocity, 4),
    'l1_haz_score': haz,
    'l1_verdict': l1,
    'l2_verdict': l2,
    'divergence': l1 != l2,
    'provenance_complete': not missing,
    **provenance,
})

wandb.finish()
print(f'Logged: d={depth}m, v={velocity}m/s | L1={l1} | L2={l2} | divergence={l1 != l2}')
