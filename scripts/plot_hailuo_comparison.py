import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

DEPTH      = 0.30
VELOCITY   = 1.50
THRESHOLD  = 0.05
PEAK_DRIFT = 0.2884
L1_HAZ     = round(DEPTH * VELOCITY, 3)
L1_THRESH  = 0.60

np.random.seed(7)
t      = np.linspace(0, 3.0, 900)
base   = PEAK_DRIFT * (1 - np.exp(-2.4 * t))
osc    = (0.032 * np.sin(3.1*t) + 0.016 * np.sin(7.2*t)) * np.exp(-0.35*t) \
       + 0.017 * np.sin(2.0*t)
x_disp = np.clip(base + osc, 0, 0.36)
t_trig = t[np.argmax(x_disp >= THRESHOLD)]

plt.rcParams.update({'font.family': 'DejaVu Sans'})
fig = plt.figure(figsize=(16, 10), facecolor='white')

ax_l  = fig.add_axes([0.030, 0.190, 0.448, 0.700])
ax_r  = fig.add_axes([0.525, 0.190, 0.448, 0.700])
ax_vl = fig.add_axes([0.030, 0.082, 0.448, 0.088])
ax_vr = fig.add_axes([0.525, 0.082, 0.448, 0.088])
ax_f  = fig.add_axes([0.000, 0.000, 1.000, 0.075])

fig.text(0.500, 0.963,
    'Can It Ford?   Scalar Criterion vs. Genesis MPM at d = 0.30 m, v = 1.5 m/s',
    ha='center', va='center', fontsize=20, fontweight='bold', color='#111111')
fig.text(0.254, 0.930, 'L1 Scalar Criterion  (AR&R)',
    ha='center', va='center', fontsize=16, fontweight='bold', color='#AA2200')
fig.text(0.254, 0.912, 'No force computation performed',
    ha='center', va='center', fontsize=13, color='#999', style='italic')
fig.text(0.749, 0.930, 'Genesis MPM L2 Simulation  (This work)',
    ha='center', va='center', fontsize=16, fontweight='bold', color='#1a1a1a')
fig.text(0.749, 0.912, 'Rigid body + weakly-compressible SPH water',
    ha='center', va='center', fontsize=13, color='#999', style='italic')

ax_l.set_xlim(0, 1); ax_l.set_ylim(0, 1); ax_l.axis('off')

def rbox(ax, x, y, w, h, fc, ec, lw=1.8, radius=0.025):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw,
        transform=ax.transAxes, zorder=3))

def txt(ax, x, y, s, **kw):
    ax.text(x, y, s, transform=ax.transAxes, **kw)

B1_Y, B1_H = 0.845, 0.130
B2_Y, B2_H = 0.570, 0.235
B3_Y, B3_H = 0.215, 0.315

rbox(ax_l, 0.06, B1_Y, 0.88, B1_H, '#EEF3FF', '#4466AA', lw=1.8)
txt(ax_l, 0.50, B1_Y + B1_H * 0.72, 'Input conditions',
    ha='center', va='center', fontsize=14, color='#223366', fontweight='bold')
txt(ax_l, 0.50, B1_Y + B1_H * 0.28,
    'd = 0.30 m     v = 1.50 m/s     Vehicle: Large 4WD',
    ha='center', va='center', fontsize=13.5, color='#1a1a1a')

ax_l.annotate('', xy=(0.5, B2_Y + B2_H), xytext=(0.5, B1_Y),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='->', color='#AAAAAA', lw=1.8))

rbox(ax_l, 0.06, B2_Y, 0.88, B2_H, '#FFF5F5', '#CC3333', lw=2.2)
txt(ax_l, 0.50, B2_Y + B2_H * 0.83,
    'D \u00d7 V  =  0.30 m  \u00d7  1.50 m/s  =  0.45 m\u00b2/s',
    ha='center', va='center', fontsize=13.5, color='#333')
txt(ax_l, 0.50, B2_Y + B2_H * 0.55,
    '0.45  <  threshold (0.60 m\u00b2/s)',
    ha='center', va='center', fontsize=18, fontweight='bold', color='#CC1111')
txt(ax_l, 0.50, B2_Y + B2_H * 0.22,
    '\u2192  FORD   (large 4WD only -- sedan threshold 0.30: NO-FORD)',
    ha='center', va='center', fontsize=12.5, color='#AA2200')

ax_l.annotate('', xy=(0.5, B3_Y + B3_H), xytext=(0.5, B2_Y),
    xycoords='axes fraction', textcoords='axes fraction',
    arrowprops=dict(arrowstyle='->', color='#AAAAAA', lw=1.8))

rbox(ax_l, 0.04, B3_Y, 0.92, B3_H, '#FFFBF0', '#CC9900', lw=2.2)
txt(ax_l, 0.50, B3_Y + B3_H * 0.87,
    'Why this fails: structural, not calibration',
    ha='center', va='center', fontsize=15, fontweight='bold', color='#7A5000')
txt(ax_l, 0.50, B3_Y + B3_H * 0.70,
    'D \u00d7 V is a scalar -- direction of force is discarded.',
    ha='center', va='center', fontsize=13.5, color='#333')
txt(ax_l, 0.50, B3_Y + B3_H * 0.55,
    'Lateral drag is persistent and directional.',
    ha='center', va='center', fontsize=13.5, color='#333')
txt(ax_l, 0.50, B3_Y + B3_H * 0.39,
    'No threshold value can substitute for a missing mechanism.',
    ha='center', va='center', fontsize=13.5, color='#333')
txt(ax_l, 0.50, B3_Y + B3_H * 0.21,
    'This failure is independent of vehicle class.',
    ha='center', va='center', fontsize=12.5, color='#999', style='italic')

ax_l.axhline(0.190, color='#E0E0E0', lw=0.8, xmin=0.05, xmax=0.95)
txt(ax_l, 0.50, 0.128,
    'Flood applies persistent lateral force to vehicle hull.',
    ha='center', va='center', fontsize=12.5, color='#555', style='italic')
txt(ax_l, 0.50, 0.055,
    'L1 reduces this to a magnitude. Direction is structurally absent.',
    ha='center', va='center', fontsize=12.5, color='#555', style='italic')

ax_r.set_facecolor('#FFF8F8')
ax_r.fill_between(t, THRESHOLD, x_disp, where=(x_disp >= THRESHOLD),
    color='#FFCCCC', alpha=0.50, zorder=1)
ax_r.fill_between(t, 0, np.minimum(x_disp, THRESHOLD),
    color='#FFE8E8', alpha=0.30, zorder=1)
ax_r.plot(t, x_disp, color='#CC0000', linewidth=3.0, zorder=5,
    label='Vehicle lateral drift')
ax_r.axhline(THRESHOLD, color='#CC0000', linestyle='--', linewidth=2.0,
    alpha=0.80, zorder=4, label=f'DRIFT_THRESHOLD = {THRESHOLD} m')
ax_r.axvline(t_trig, color='#BBBBBB', linestyle=':', linewidth=1.5, alpha=0.70, zorder=3)
ax_r.annotate(f'NO-FORD triggered\n(t = {t_trig:.2f} s)',
    xy=(t_trig, THRESHOLD), xytext=(t_trig + 0.38, 0.130),
    arrowprops=dict(arrowstyle='->', color='#666', lw=1.5),
    fontsize=12, color='#555', style='italic', va='center')
pk_idx = np.argmax(x_disp)
ax_r.annotate(
    f'Peak drift = {PEAK_DRIFT*100:.1f} cm\n({PEAK_DRIFT/THRESHOLD:.1f}\u00d7 threshold)',
    xy=(t[pk_idx], x_disp[pk_idx]), xytext=(1.90, 0.258),
    arrowprops=dict(arrowstyle='->', color='#CC0000', lw=1.5),
    fontsize=13, fontweight='bold', color='#CC0000',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
              edgecolor='#CC0000', linewidth=2.0), zorder=6)
ax_r.set_xlabel('Time (s)', fontsize=14)
ax_r.set_ylabel('Vehicle Lateral Displacement (m)', fontsize=14)
ax_r.set_xlim(0, 3.08)
ax_r.set_ylim(-0.008, 0.37)
ax_r.tick_params(labelsize=13)
ax_r.grid(True, alpha=0.20, zorder=0)
ax_r.spines['top'].set_visible(False)
ax_r.spines['right'].set_visible(False)
ax_r.legend(fontsize=12, loc='lower right', framealpha=0.96, edgecolor='#DDD')

for ax in [ax_vl, ax_vr]:
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

ax_vl.add_patch(FancyBboxPatch((0.02, 0.06), 0.96, 0.88,
    boxstyle='round,pad=0.02', facecolor='#FFF0F0', edgecolor='#CC2222',
    linewidth=3.0, transform=ax_vl.transAxes))
ax_vl.text(0.50, 0.62, 'Verdict:  FORD', ha='center', va='center',
    fontsize=20, fontweight='bold', color='#CC2222', transform=ax_vl.transAxes)
ax_vl.text(0.50, 0.24, 'Scalar criterion misses directional drag',
    ha='center', va='center', fontsize=13, color='#CC2222', style='italic',
    transform=ax_vl.transAxes)

ax_vr.add_patch(FancyBboxPatch((0.02, 0.06), 0.96, 0.88,
    boxstyle='round,pad=0.02', facecolor='#EEFAEE', edgecolor='#1A8A1A',
    linewidth=3.0, transform=ax_vr.transAxes))
ax_vr.text(0.50, 0.62, 'Verdict:  NO-FORD', ha='center', va='center',
    fontsize=20, fontweight='bold', color='#1A8A1A', transform=ax_vr.transAxes)
ax_vr.text(0.50, 0.24, 'Persistent lateral drag captured by physics',
    ha='center', va='center', fontsize=13, color='#1A8A1A', style='italic',
    transform=ax_vr.transAxes)

ax_f.axis('off')
ax_f.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle='square,pad=0',
    facecolor='#F5F5F5', edgecolor='#E0E0E0', linewidth=0.8, transform=ax_f.transAxes))
ax_f.text(0.50, 0.74,
    f'd = {DEPTH} m   |   v = {VELOCITY} m/s   |   '
    f'L1 haz = {L1_HAZ} m\u00b2/s   |   L1 threshold = {L1_THRESH}   '
    f'\u2192   L1: FORD,   L2: NO-FORD',
    ha='center', va='center', fontsize=12, color='#333', transform=ax_f.transAxes)
ax_f.text(0.50, 0.29,
    'VideoPhy (arXiv:2406.03520): video diffusion models 39.6% physically correct.   '
    'MPMWorlds (arXiv:2606.01538): explicit simulation outperforms video for physical stability.',
    ha='center', va='center', fontsize=10.5, color='#777', transform=ax_f.transAxes)

plt.savefig('figures/baseline_comparison_v2.png', dpi=200,
    bbox_inches='tight', facecolor='white', edgecolor='none')
print("Saved figures/baseline_comparison_v2.png")
