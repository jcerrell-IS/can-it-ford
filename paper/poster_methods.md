# Methods

## How the pipeline works

I start with a real video of a flooded road and turn it into a 3D model of the scene using Gaussian splatting. That geometry then feeds a physics simulation that treats the water and the vehicle as thousands of tiny particles (the Material Point Method, or MPM). The water pushes on the vehicle and the vehicle pushes back, so effects like the vehicle getting lighter as it starts to float, or getting shoved sideways by the current, come out of the physics on their own instead of me putting them in by hand.

## The vehicle I actually tested (honest version)

The results here use a **box-proxy vehicle**, not a full car mesh yet. I take a simple block and stretch it so its mass, size, displaced water volume, and side-on area match a real vehicle class. I ran a **compact sedan (1390 kg)** and a **light pickup (2300 kg)**. I also ran a midsize SUV but dropped it, because once it was filled in its density came out physically unrealistic. Because the sedan is 1390 kg and 4.66 m long, it lands in the **Large passenger car** class in the flood-safety guidelines, not the "Small Car" class a tiny subcompact would.

I am also wiring in a **real Toyota Yaris car mesh** as the next step, but it has **not** produced a validated result yet (I found a mass bug and it is still being checked), so it is not a claim on this poster, just work in progress.[^yaris]

[^yaris]: The Yaris mesh's own modeled weight is 1078 kg. The 1100 kg figure sometimes quoted for this car is the MASH nominal test-class standard, a slightly different number.

## The three levels I compare

The whole point is to find the simplest model that still gets the ford / no-ford answer right, so I test three levels of detail:

- **L0**: just a depth cutoff. Deeper than a set number means no.
- **L1**: depth times speed (H = D x V), from the Australian flood-safety guidelines. This adds flow speed, not just depth.
- **L2**: the full particle simulation, where floating and sliding come out of the actual water-and-vehicle interaction.

## Which simulator did what (honest status)

Two solvers actually produced results here, and the one I ultimately want is still broken. I want to be straight about which is which:

- **Genesis SPH pilot** (a simpler, water-only stand-in using plain box shapes): this produced my main finding, that L1 and L2 disagree in fast, shallow water, and that changing the tire friction does not fix that disagreement.
- **kks32/mpm-engine** (the Kumar group's MPM solver): this extends the same logic to the full box-proxy vehicle classes above and reports how far the vehicle slides. It is the solver I cite for the vehicle sweep.
- **Genesis coupled-MPM** (the real goal, a car mesh fully coupled to MPM water): **not working yet.** It crashes at the particle-to-grid step and produced none of the results here. That is honest open work, not a finished capability.

## Where it runs

Everything runs on GPU nodes at TACC: Lonestar6 for the 3D reconstruction and Vista for the simulations.
