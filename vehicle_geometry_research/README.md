# Vehicle geometry

The 17 coupled runs use `yaris_coarse_v1l_watertight.ply`, a watertight hull derived from the
**2010 Toyota Yaris coarse finite element model (v1l)**. That model was developed by the Center for
Collision Safety and Analysis (CCSA) at George Mason University, with sponsorship from the Federal
Highway Administration (FHWA). Model documentation: DOI
[10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D).

## What is here

| Path | What it is |
|---|---|
| `yaris_coarse_v1l_watertight.ply` | The hull every reported run used |
| `2010-toyota-yaris-coarse-v1l/`, `2010-toyota-yaris-detailed-v2j/` | Upstream CCSA Yaris finite element models, and their archives |
| `2007-chevrolet-silverado-coarse-v3a/`, `2007-chevrolet-silverado-detailed-v3e/` | Upstream CCSA Silverado models, and their archives |
| `WATERTIGHT_HULL_TOOL_FINDINGS.md` | Notes from producing the watertight hull |
| `failed_reconstructions_2026-07-25/` | Superseded reconstruction attempts, kept as a record |

## Check that you have the same hull the runs used

Its SHA-256 is `b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95`, and the same hash
is recorded for every run in `data/reproducibility_manifest.json`.

```bash
shasum -a 256 vehicle_geometry_research/yaris_coarse_v1l_watertight.ply
```

## Acknowledgement

As the model's authors request, this project acknowledges the CCSA at George Mason University and
the FHWA for the finite element model. The model's own documentation states that users must verify
their own simulations, and that neither CCSA nor FHWA assumes responsibility for results obtained
from it. Terms for every third-party item in this repository are listed in
[`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
