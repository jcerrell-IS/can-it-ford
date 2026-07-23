# Files to Pull Into can-it-ford, Verified Working Links

Every link below was live-checked (HTTP 200) before being included. Where a file needs extra processing before it's usable, that's stated, not hidden.

---

## From the Genesis/kks32 research report, code you already have access to

These aren't separate downloads, they're specific files inside `kks32/mpm-engine`, which you already have cloned on Vista. Worth pulling up directly to see if the splat bridge already does what you need:

- `src/warpmpm/splats/` — the Gaussian splat simulation package
  https://github.com/kks32/mpm-engine/tree/main/src/warpmpm/splats
- `examples/splat_sim.py` — the working example that runs it
  https://github.com/kks32/mpm-engine/blob/main/examples/splat_sim.py
- `src/warpmpm/vehicle.py` — contains `load_vehicle()`, which loads a splat PLY as a rigid vehicle body, and `FloodScene`, the shallow-water class
  https://github.com/kks32/mpm-engine/blob/main/src/warpmpm/vehicle.py

## New external tool worth adding

- **splashsurf**, particle-to-mesh surface reconstruction, the real tool for turning MPM/SPH particle output into a renderable surface
  Repo: https://github.com/InteractiveComputerGraphics/splashsurf
  On Vista, check whether it builds clean on aarch64 before counting on it, prebuilt Python wheels don't clearly cover that architecture, may need `cargo build` from source.

---

## Vehicle files, honest breakdown

**Important, same caveat that applied to your Yaris mesh:** none of the NCAC/CCSA models below are ready-to-use PLY files. They're LS-DYNA finite-element models (`.k` keyword files) that need the same watertightening/conversion pipeline you already built once (mesh2sdf, hull tool). Budget for that step, don't expect to drop these straight into a sim.

**If you want something that works today with zero conversion pipeline:** scan a real car with Scaniverse (verified two turns ago: on-device Gaussian Splat capture, exports PLY directly), and load it straight into `kks32/mpm-engine`'s `load_vehicle()`. That's the fast, fun, guaranteed-no-genus-9-marching-cubes-disaster path. Any car you think looks cool, in person, works.

**If you want something crash-validated and government-sourced**, here are the real options from the same official archive your Yaris came from ([full catalog](https://www.ccsa.gmu.edu/models/)):

### Already resolved, no action needed
- **2010 Toyota Yaris** (1100C class), already converted, already your canonical vehicle mesh (`yaris_coarse_v1l_watertight.ply`).

### The cool option, recommended if you want a second vehicle
- **2018 Dodge Ram pickup**, real weight 2,337 kg, MASH 2270P class
  Page: https://www.ccsa.gmu.edu/models/2018-dodge-ram/
  Coarse model (recommended, matches the resolution level that worked for Yaris): https://media.ccsa.gmu.edu/model/2018-dodge-ram-coarse-v3d.zip (22.2 MB, 835K elements)
  Detailed model (heavier, likely painful at MPM particle resolution): https://media.ccsa.gmu.edu/model/2018-dodge-ram-detailed-v3a.zip (67.3 MB, 2.68M elements)
  Checksum (coarse, SHA512-256): `bd6dab87d5a3f91cf64bda68591158bb273279ff539016b835ef858070c181bd`

### SUV middle ground
- **2020 Nissan Rogue**, real weight 1,609 kg
  Page: https://www.ccsa.gmu.edu/models/2020-nissan-rogue/
  Download: https://media.ccsa.gmu.edu/model/2020-nissan-rogue-v3.zip (72.3 MB, 3.24M elements, only one resolution offered, no coarse variant)
  Checksum (SHA384): `968cd10ebe15a61aab3dc0e58c063bea7acd48388f72ed25624c3ef1dfd6197e94ea06ae1cd7524b66063ebbb56925c4`

Both are real vehicles with real, documented curb weights, not placeholders, and both are visually a lot more interesting than the Yaris if what you want is something that looks good in a render.

---

## My actual recommendation, one line

Don't run both conversion pipelines tonight. Scan something cool with Scaniverse for the fun, fast, guaranteed-to-work render. Keep the Ram or Rogue as a someday-if-there's-time addition, not tonight's task, they're real files sitting at real verified links whenever you want them, they're not going anywhere.
