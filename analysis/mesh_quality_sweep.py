#!/usr/bin/env python3
"""Rank candidate vehicle hulls for RENDERING, on two opposing criteria.

WHY TWO. Minimising surface roughness alone selects a BLOB. The smoothest Rogue on
this machine is rogue_g96_pd6 at 9.75 deg mean dihedral, near the Yaris's 7.61, and
it is missing 47.6 percent of the vehicle's volume: a low Poisson depth is smooth
precisely because it has stopped following the surface. Volume is also the quantity
the buoyancy argument rests on. So: volume error within a few percent as a HARD GATE,
then minimum dihedral among the survivors.

AND ONE METRIC HERE IS A TRAP, which is why the normalised column exists. Taubin
displacement is NOT resolution-independent: it scales with edge length, because
smoothing moves a vertex toward neighbours that are further away on a coarse mesh.
Across 20 meshes Taubin/edge sits in 0.268 to 0.351 while the raw value spans 4.66 to
76.70 mm, so the raw number is close to a measure of triangle size. Mean DIHEDRAL
angle is dimensionless and is the one to rank on.
"""
import glob, os, numpy as np, trimesh
D="/Users/josie/Downloads/vehicle_meshes/"
R="/Users/josie/can-it-ford/vehicle_geometry_research/"
SIMVOL={"rogue":4.9601703806221,"silverado":7.943659119387191,"yaris":3.5513843861695054}
files=sorted(glob.glob(D+"*coarse_watertight.ply"))+[R+"yaris_coarse_v1l_watertight.ply"]
print("%-44s %7s %7s %8s %8s %8s"%("mesh","edge_mm","rough_mm","rough/edge","vol_err%","dihed_deg"))
print("-"*92)
for f in files:
    m=trimesh.load(f,process=False)
    V=np.asarray(m.vertices,dtype=np.float64); F=np.asarray(m.faces)
    e=np.linalg.norm(V[F[:,0]]-V[F[:,1]],axis=1)
    edge=float(np.median(e))*1000.0
    s=trimesh.Trimesh(vertices=V.copy(),faces=F.copy(),process=False)
    trimesh.smoothing.filter_taubin(s,lamb=0.5,nu=0.53,iterations=60)
    rough=float(np.linalg.norm(np.asarray(s.vertices)-V,axis=1).mean())*1000.0
    # dihedral angle between adjacent faces: a RESOLUTION-INDEPENDENT roughness measure
    fa=m.face_adjacency_angles
    dih=float(np.degrees(np.mean(fa))) if len(fa) else float("nan")
    key=[k for k in SIMVOL if k in os.path.basename(f)]
    verr=100.0*(abs(float(m.volume))-SIMVOL[key[0]])/SIMVOL[key[0]] if key else float("nan")
    print("%-44s %7.1f %7.2f %8.3f %8.2f %8.2f"%(os.path.basename(f),edge,rough,rough/edge,verr,dih))
