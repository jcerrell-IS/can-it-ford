import argparse
import wandb

PROVENANCE_FIELDS = [
    "n_grid", "dx", "water_layers", "solid_volume", "realized_rho",
    "water_eta", "floor_friction", "vehicle_asset", "vehicle_mass_kg",
]

ap = argparse.ArgumentParser()
ap.add_argument("depth", type=float)
ap.add_argument("velocity", type=float)
ap.add_argument("l2", choices=["FORD", "NO-FORD"])
ap.add_argument("--n-grid", type=int, default=None)
ap.add_argument("--dx", type=float, default=None)
ap.add_argument("--water-layers", type=int, default=None)
ap.add_argument("--solid-volume", type=float, default=None)
ap.add_argument("--realized-rho", type=float, default=None)
ap.add_argument("--water-eta", type=float, default=None)
ap.add_argument("--floor-friction", type=float, default=None)
ap.add_argument("--vehicle-asset", default=None)
ap.add_argument("--vehicle-mass-kg", type=float, default=None)
args = ap.parse_args()

depth = args.depth
velocity = args.velocity
l2 = args.l2
l1 = "FORD" if depth * velocity <= 0.60 else "NO-FORD"
haz = round(depth * velocity, 3)

provenance = {f: getattr(args, f) for f in PROVENANCE_FIELDS}
missing = [f for f, v in provenance.items() if v is None]

wandb.init(
    project="can-it-ford",
    entity="jcerrell29-claremont-mckenna-college",
    name=f"L2_d{depth}_v{velocity}",
    tags=["L2", "Genesis-MPM", "Vista"],
    config={
        "depth_m": depth,
        "velocity_ms": velocity,
        "l1_threshold": 0.60,
        "level": "L2_Genesis_SPH",
        "compute": "Vista_GH200",
        **provenance,
    },
)

wandb.log({
    "depth_m": depth,
    "velocity_ms": velocity,
    "dv_product": round(depth * velocity, 4),
    "l1_haz_score": haz,
    "l1_verdict": l1,
    "l2_verdict": l2,
    "divergence": l1 != l2,
    "provenance_complete": not missing,
    **provenance,
})

wandb.finish()
print(f"Logged: d={depth}m, v={velocity}m/s | L1={l1} | L2={l2} | divergence={l1!=l2}")
if missing:
    print(f"PROVENANCE INCOMPLETE, {len(missing)} unset: {', '.join(missing)}")
