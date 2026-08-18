#!/usr/bin/env python3
"""Independently re-derive the review-supplied figures in docs/R7_PINNED_SPAN_LADDER_2026-08-18.md.

An adversarial review supplied several numbers (the constant-depth power law, the 7-layer
excess, depth elasticities, the collinearity ratio, fetch drift, water-block width). Claim
discipline says a number from another agent is not a verified number, so every one of them
is recomputed here from the run data before it is allowed into the document.

Run:  /opt/homebrew/bin/uv run --with numpy python3 analysis/r7_verify_doc_numbers.py <staged>
"""
import sys, json, glob, math
from pathlib import Path
REPO = Path("/Users/josie/can-it-ford/.claude/worktrees/r7-pinned-span")
sys.path.insert(0, str(REPO/"simulation"))
import numpy as np, failure_modes as FM
b = Path(sys.argv[1])
S = 9.421742313727737*(1-8/48); CLEAR = 0.1774

def reps(d):
    out=[]
    for p in sorted(glob.glob(str(Path(d)/"rep_*/metrics.csv"))):
        k=FM.kinematics_from_columns(FM.load_timeseries(p),2337.0)
        out.append(float(np.max(np.abs(k.disp[:,FM.SURGE_AXIS]))))
    return out
def summ(d): return json.load(open(sorted(glob.glob(str(Path(d)/"rep_*/summary.json")))[0]))

EX = {3:"r7_pin_g48_exact_918475",6:"r7_pin_g88_exact_918488",9:"r7_pin_g128_exact_918490",
      12:"r7_pin_g168_exact_918493",15:"r7_pin_g208_exact_918495"}
print("=== 1. constant-depth exact sub-ladder, MEAN drift, power-law fit ===")
L=[];D=[]
for k in sorted(EX):
    r=reps(b/EX[k]); L.append(k); D.append(np.mean(r))
    print("  %2d layers  mean %.6f  max %.6f" % (k, np.mean(r), max(r)))
lg=np.polyfit(np.log(L),np.log(D),1)
print("  fit: drift = %.5f * layers^%.4f" % (math.exp(lg[1]), lg[0]))
pred=lambda x: math.exp(lg[1])*x**lg[0]
print("  residuals %%: %s" % ["%+.1f"%(100*(d/pred(l)-1)) for l,d in zip(L,D)])
print("  fall 3->15 layers: %.2f %% (factor %.3f) on mean, %.2f %% on max"
      % (100*(1-D[-1]/D[0]), D[0]/D[-1], 100*(1-max(reps(b/EX[15]))/max(reps(b/EX[3])))))

print()
print("=== 2. the 7-layer outlier against that trend ===")
r96=reps(b/"r7_pin_g96_free_918489"); m96=np.mean(r96)
print("  pin g96 (7 layers) mean %.6f, trend predicts %.6f, excess %+.1f %%"
      % (m96, pred(7), 100*(m96/pred(7)-1)))
print("  required depth elasticity to close it: %.2f" % ((m96/pred(7)-1)/0.06061))

print()
print("=== 3. measurable depth elasticities at fixed layer count ===")
for lab,a,c,la in (("12 layers pin160free vs pin168exact","r7_pin_g160_free_918492","r7_pin_g168_exact_918493",12),
                   ("4 layers unp g64 vs pin g64 free","r6_rep_g64_918249","r7_pin_g64_free_918487",4)):
    sa,sc=summ(b/a),summ(b/c); da,dc=np.mean(reps(b/a)),np.mean(reps(b/c))
    dpa=sa["water_layers"]*sa["h"]; dpc=sc["water_layers"]*sc["h"]
    dd=(dpa/dpc-1); dr=(da/dc-1)
    print("  %-38s depth %+.2f%% -> drift %+.2f%%  elasticity %.2f" % (lab,100*dd,100*dr,dr/dd if dd else float('nan')))

print()
print("=== 4. tank gap between unp g128 (8 layers) and pin g128 (9 layers) ===")
u,p_=summ(b/"r6_rep_g128_918247"),summ(b/"r7_pin_g128_exact_918490")
uv=u["n_water"]*u["h"]**3; pv=p_["n_water"]*p_["h"]**3
print("  unp %.4f m3 vs pin %.4f m3  = %+.2f %%" % (uv,pv,100*(uv/pv-1)))

print()
print("=== 5. clearance-particles / depth-layers collinearity, exact rungs ===")
for k in sorted(EX):
    s=summ(b/EX[k]); print("  %2d layers  clearance/h = %.6f  ratio = %.6f" % (k, CLEAR/s["h"], (CLEAR/s["h"])/k))

print()
print("=== 6. upstream fetch and initial gap ===")
def fetch(lim,n): return 0.60*lim-4.0*(lim/n)
for lab,rows in (("unpinned",[(48,9.421742313727737),(192,9.421742313727737)]),
                 ("pinned  ",[(48,S*48/40),(192,S*192/184)])):
    f=[fetch(l,n) for n,l in rows]
    print("  %s fetch g48 %.4f -> g192 %.4f  %+.2f %%" % (lab,f[0],f[1],100*(f[1]/f[0]-1)))
print("  initial gap 0.5h: n=48 %.1f mm -> n=208 %.1f mm" %
      (500*summ(b/EX[3])["h"], 500*summ(b/EX[15])["h"]))

print()
print("=== 7. water block width (2n-17)*h vs S ===")
for lab,dirs in (("pinned",[(48,"r7_pin_g48_exact_918475"),(208,"r7_pin_g208_exact_918495")]),
                 ("unpinned",[(48,"r6_rep_g48_918250"),(192,"r6_rep_g192_918351")])):
    w=[]
    for n,d in dirs:
        s=summ(b/d); tot=s["n_water"]+s["n_carved"]; cols=math.isqrt(tot//s["water_layers"])
        w.append(cols*s["h"])
    print("  %-9s %.6f -> %.6f  %+.2f %%" % (lab,w[0],w[1],100*(w[1]/w[0]-1)))
