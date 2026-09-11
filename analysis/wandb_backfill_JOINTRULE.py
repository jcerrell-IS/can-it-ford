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

EXPECT_ROWS = 70
EXPECT_JOINT_FORD = 14
EXPECT_BARE_FORD = 37
EXPECT_RECLASS = 23

ap = argparse.ArgumentParser()
ap.add_argument('--push', action='store_true',
                help='actually write to wandb.ai; without this flag nothing leaves this machine')
args = ap.parse_args()

runs = [
    {'depth_m': 0.15, 'velocity_ms': 0.0, 'verdict': 'FORD'},
    {'depth_m': 0.30, 'velocity_ms': 0.0, 'verdict': 'FORD'},
    {'depth_m': 0.60, 'velocity_ms': 0.0, 'verdict': 'FORD'},
    {'depth_m': 0.15, 'velocity_ms': 1.5, 'verdict': 'NO-FORD'},
    {'depth_m': 0.30, 'velocity_ms': 1.5, 'verdict': 'NO-FORD'},
    {'depth_m': 0.45, 'velocity_ms': 1.5, 'verdict': 'NO-FORD'},
    {'depth_m': 0.60, 'velocity_ms': 1.5, 'verdict': 'NO-FORD'},
    {'depth_m': 0.30, 'velocity_ms': 1.0, 'verdict': 'NO-FORD'},
    {'depth_m': 0.30, 'velocity_ms': 2.0, 'verdict': 'NO-FORD'},
]


def joint_rule(d, v):
    if d <= JOINT_DEPTH_CAP and v <= JOINT_VEL_CAP and round(d * v, 6) <= JOINT_PRODUCT_CAP:
        return 'FORD'
    return 'NO-FORD'


with open(SWEEP_CSV, newline='', encoding='utf-8-sig') as fh:
    sweep_rows = list(csv.DictReader(fh))

sweep_table = {}
for r in sweep_rows:
    sweep_table[(round(float(r['depth_m']), 6), round(float(r['velocity_ms']), 6))] = r['L1_verdict']

joint_ford = sum(1 for r in sweep_rows if r['L1_verdict'] == 'FORD')
bare_ford = sum(1 for r in sweep_rows if r['L1_haz_product_only'] == 'FORD')
reclass = sum(1 for r in sweep_rows
              if r['L1_haz_product_only'] == 'FORD' and r['L1_verdict'] == 'NO-FORD')
reverse = sum(1 for r in sweep_rows
              if r['L1_haz_product_only'] == 'NO-FORD' and r['L1_verdict'] == 'FORD')

print('L1 JOINT RULE AUDIT, source data/scenario_sweep.csv')
print(f'  rows {len(sweep_rows)}, joint FORD {joint_ford}, bare FORD {bare_ford}, '
      f'reclassified {reclass}, reverse {reverse}')
assert len(sweep_rows) == EXPECT_ROWS
assert joint_ford == EXPECT_JOINT_FORD
assert bare_ford == EXPECT_BARE_FORD
assert reclass == EXPECT_RECLASS
assert reverse == 0

payloads = []
for r in runs:
    d, v = float(r['depth_m']), float(r['velocity_ms'])
    key = (round(d, 6), round(v, 6))
    if key in sweep_table:
        l1_verdict, source = sweep_table[key], 'scenario_sweep.csv'
    else:
        l1_verdict, source = joint_rule(d, v), 'joint rule, not in the sweep grid'
    l1_haz = round(d * v, 3)
    divergence = (r['verdict'] == 'NO-FORD' and l1_verdict == 'FORD')
    payloads.append({
        'name': f'd{r["depth_m"]}_v{r["velocity_ms"]}',
        'depth_m': d,
        'velocity_ms': v,
        'L1_verdict': l1_verdict,
        'L1_rule': 'joint: depth <= 0.30 m AND velocity <= 3.0 m/s AND D*V <= 0.30 m2/s',
        'L1_source': source,
        'L1_hazard_product': l1_haz,
        'L2_verdict': r['verdict'],
        'L1_L2_divergence': divergence,
    })

print()
print('PAYLOADS')
for p in payloads:
    print(f'  {p["name"]:16s} L1={p["L1_verdict"]:8s} L2={p["L2_verdict"]:8s} '
          f'divergence={str(p["L1_L2_divergence"]):5s} source={p["L1_source"]}')

n_div = sum(1 for p in payloads if p['L1_L2_divergence'])
print()
print(f'divergent cells under the joint rule: {n_div} of {len(payloads)}')

if not args.push:
    print()
    print('DRY RUN. Nothing was sent to wandb.ai. Re-run with --push to write.')
    sys.exit(0)

import wandb

wandb.login(key=os.environ.get('WANDB_API_KEY'))
for p in payloads:
    run = wandb.init(
        project='can-it-ford',
        entity=ORG,
        name=p['name'],
        config={
            'depth_m': p['depth_m'],
            'velocity_ms': p['velocity_ms'],
            'vehicle_class': 'small_passenger',
            'L1_rule': p['L1_rule'],
            'L1_source': p['L1_source'],
            'drift_threshold_m': 0.05,
        },
        reinit=True,
    )
    wandb.log({
        'L2_verdict': 1 if p['L2_verdict'] == 'FORD' else 0,
        'L1_verdict': 1 if p['L1_verdict'] == 'FORD' else 0,
        'L1_hazard': p['L1_hazard_product'],
        'depth_m': p['depth_m'],
        'velocity_ms': p['velocity_ms'],
        'L1_L2_divergence': int(p['L1_L2_divergence']),
    })
    wandb.summary.update({
        'verdict': p['L2_verdict'],
        'L1_verdict': p['L1_verdict'],
        'L1_rule': p['L1_rule'],
        'divergence': p['L1_L2_divergence'],
    })
    run.finish()
    print(f'Logged {p["name"]}')

print(f'\nDone. https://wandb.ai/{ORG}/can-it-ford')
