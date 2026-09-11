# Vehicle geometry (not included)

The 17 coupled simulation runs use a watertight hull derived from the **2010 Toyota Yaris coarse
finite element model (v1l)**. The model was developed by the Center for Collision Safety and
Analysis (CCSA) at George Mason University, with sponsorship from the Federal Highway
Administration (FHWA). Model documentation: DOI
[10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D).

The upstream model files carry no redistribution licence. Neither the model nor the hull derived
from it is included in this repository. Scripts that load
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` expect you to place your own copy in
this folder. The conversion from the upstream model to the watertight hull is not included either.

**To obtain the model:** download the 2010 Toyota Yaris coarse model from CCSA,
<https://www.ccsa.gmu.edu/>.

**To check that you have the same hull the runs used:** the file used for all 17 runs has SHA-256
`b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95`. The same hash is recorded for
every run in `data/reproducibility_manifest.json`.

```bash
shasum -a 256 vehicle_geometry_research/yaris_coarse_v1l_watertight.ply
```

**Acknowledgement.** As the model's authors request, this project acknowledges the CCSA at George
Mason University and the FHWA for the finite element model. The model's own documentation states
that users must verify their own simulations, and that neither CCSA nor FHWA assumes
responsibility for results obtained from it.
