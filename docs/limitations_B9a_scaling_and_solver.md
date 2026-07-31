# Limitations: scaling, solver compressibility, and resolution

Written 2026-07-25 per AMENDMENT B item B9a. Every number below was computed or
read at source in the session that wrote this file. Nothing is carried from a
summary.

Source for the scaling block: `examples/flood_vehicle.py` docstring,
kks32/mpm-engine, pinned SHA `544c93dd02cb9c7ead89e1155a62967243244fce`,
archived at `third_party/mpm-engine-544c93dd/examples/flood_vehicle.py`.

## 1. Froude scaling, and why it does not apply to these runs

Kumar's docstring states the standard free-surface similitude. With length ratio
`lam = L_real / L_model`, quoting the source lines 14 to 16:

> length, depth, displacement x lam; velocity, time x sqrt(lam); mass, force x lam^3

The docstring also records the two caveats that come with it: "Reynolds number is
not matched, as in any Froude model, and the water viscosity here is inflated for
stability anyway", with the justification that the vehicle response is dominated
by the inertial momentum flux `rho v^2 h`, which Froude scaling preserves.

**Neither caveat transfers to this project's runs, and the reason should be
stated rather than left implicit.** The docstring's own escape hatch is "To skip
the conversion, run at full scale directly". That is what these runs do:

| quantity | value in these runs | measured from |
|---|---|---|
| vehicle length | 4.2826 m, native mesh, no `target_length` | mesh vertices |
| water depth | 0.30 m | `npz["depth"]` |
| vehicle mass | 1100 / 1609 / 2337 kg | run configs |
| water viscosity | 1.0e-3 Pa s | `sim_standing.py:75`, `:226` |

The upstream default is `water_eta = 1.0` Pa s (`vehicle_main.py:224`), which is
1000x real water and is the "inflated for stability" value the docstring refers
to. **This project overrides it to 1.0e-3 Pa s, the physical value, and passes it
explicitly.** So there is no Froude conversion to invert and no inflated
viscosity to discount. Any Limitations text claiming otherwise would be wrong.

What remains as genuine limitations is numerical, not similitude, and is below.

## 2. Weakly compressible water

The solver uses a weakly compressible Newtonian fluid with an artificial bulk
modulus (`sim_standing.py:75`, `:128`, recorded to the run manifest at `:355`).

| quantity | simulated | real water | ratio |
|---|---|---|---|
| bulk modulus K | 1.5e5 Pa | 2.2e9 Pa | 1 : 14,667 |
| sound speed `c = sqrt(K/rho)` | 12.25 m/s | 1483 m/s | 1 : 121 |

The artificial sound speed sets a Mach number for the flow, and density variation
scales as roughly `Ma^2`:

| flow speed | Ma | approximate density variation |
|---|---|---|
| 1.5 m/s | 0.122 | 1.5% |
| 3.0 m/s (the AR&R velocity cap) | 0.245 | 6.0% |

This is the standard weakly compressible trade: a real sound speed would force a
timestep about 121x smaller. The consequence to state plainly is that **at the
top of the AR&R velocity range the fluid is about 6% compressible**, so buoyancy
and pressure-driven forces there carry a systematic error of that order. Runs at
1.5 m/s and below sit near the conventional 1% guidance and are not materially
affected.

## 3. Grid and particle resolution, and the water column

With `n_grid = 64` on a domain of `lim = 9.4217 m`:

| quantity | value |
|---|---|
| grid spacing dx | 0.147215 m |
| particle pitch h = dx/2 | 0.073607 m |
| vehicle length in grid cells | 29.1 |
| vehicle length in particle pitches | 58.2 |
| **water depth (0.30 m) in grid cells** | **2.04** |
| **water depth in particle pitches** | **4.08, giving 4 particle layers** |

The vehicle is well resolved. **The water column is not.** A 0.30 m flood is two
grid cells deep. Free-surface position, and therefore the wetted area driving
buoyancy, is quantised at roughly the 0.147 m grid spacing, which is half the
total depth being modelled. This is the single largest numerical limitation in
the current sweep and it should be stated first, ahead of compressibility.

It also interacts with vehicle class. Because `lim` is derived from the vehicle
extent, rescaling the vehicle changes dx and therefore the layer count: measured
4, 4 and 3 layers for small passenger, large passenger and large 4WD
respectively. See the confound note in
`RENDER_V1_AMENDMENT_A_PROCESS_2026-07-25.md` section A6.

## 4. Boundary layers are not resolved, and that is acceptable

At `nu = 1.0e-6 m2/s` and v = 1.5 m/s over the 4.2826 m body, `Re = 6.42e6`. A
laminar estimate `delta ~ L/sqrt(Re)` gives **1.69 mm** against `dx = 147.2 mm`,
so the boundary layer is unresolved by a factor of about **87**.

This is worth stating but not worth apologising for. Following the reasoning in
Kumar's own docstring, the vehicle response in this regime is dominated by the
inertial momentum flux `rho v^2 h` rather than by skin friction, and that term is
resolved. Skin-friction drag is not, so any conclusion that depends on viscous
drag rather than form drag and buoyancy is out of scope for this model.

## 5. Sampling non-determinism in the vehicle frame

`load_vehicle` computes the vehicle-frame shift from `mesh.sample(60_000)`, which
is **unseeded**. The vehframe transform, the solid particle count, and therefore
the effective vehicle density are not bit-reproducible across runs for mesh
inputs.

Measured magnitude for this asset: the residual between the vertex-derived extent
and the stored `npz["extent"]` is **2.030e-07 m**, which is **0.43 float32 ulp**
at 4.28 m. So for this mesh the effect is below the storage precision of the
value it perturbs, and it did not move the discretization. The defect is real and
should be reported; its measured magnitude here is negligible. A seed should be
added upstream regardless, because the magnitude is not guaranteed for a coarser
or less uniform mesh.
