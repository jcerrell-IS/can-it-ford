import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('data/phase_space_results.csv')
df = df.drop_duplicates(subset=['depth_m', 'velocity_ms'], keep='last')

df['L1_haz'] = df['depth_m'] * df['velocity_ms']
df['L1_verdict'] = df['L1_haz'].apply(lambda h: 'FORD' if h < 0.60 else 'NO-FORD')

def classify(row):
    if row['verdict'] == 'FORD'    and row['L1_verdict'] == 'FORD':    return 'FORD_AGREE'
    if row['verdict'] == 'NO-FORD' and row['L1_verdict'] == 'NO-FORD': return 'NOFORD_AGREE'
    if row['verdict'] == 'NO-FORD' and row['L1_verdict'] == 'FORD':    return 'DIVERGE'
    return 'OTHER'

df['category'] = df.apply(classify, axis=1)

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_facecolor('#fafafa')

d_arr = np.linspace(0.07, 0.75, 500)

v_thresh_4wd = np.minimum(0.60 / d_arr, 3.0)
ax.fill_between(d_arr, 0, v_thresh_4wd,   alpha=0.10, color='#4dac26')
ax.fill_between(d_arr, v_thresh_4wd, 3.0, alpha=0.08, color='#d01c8b')

for thresh, label, ls, col, lw in [
    (0.30, 'AR&R sedan (0.30 m\u00b2/s)',       ':',  '#1a6faf', 1.6),
    (0.45, 'AR&R large pass. (0.45 m\u00b2/s)', '--', '#4393c3', 1.6),
    (0.60, 'AR&R 4WD (0.60 m\u00b2/s)',         '-',  '#e07b00', 2.4),
]:
    ax.plot(d_arr, thresh / d_arr, color=col, lw=lw, linestyle=ls, label=label, zorder=4)

ax.axvline(0.15, color='#333333', lw=1.4, linestyle='--',
           label='L0 depth threshold (0.15 m)', zorder=3)





ford     = df[df['category'] == 'FORD_AGREE']
agree_no = df[df['category'] == 'NOFORD_AGREE']
diverge  = df[df['category'] == 'DIVERGE']

ax.scatter(ford['depth_m'], ford['velocity_ms'],
           color='#4dac26', marker='o', s=140, zorder=7,
           label='L2 = FORD  (L1 agrees)',
           edgecolors='#2d7a16', linewidths=1.3)
ax.scatter(agree_no['depth_m'], agree_no['velocity_ms'],
           color='#c0392b', marker='X', s=140, zorder=7,
           label='L2 = NO-FORD  (L1 agrees)',
           edgecolors='#922b21', linewidths=1.3)
ax.scatter(diverge['depth_m'], diverge['velocity_ms'],
           color='#e07b00', marker='D', s=180, zorder=8,
           label='DIVERGE: L1=FORD, L2=NO-FORD',
           edgecolors='#333333', linewidths=1.2)
ax.scatter(diverge['depth_m'], diverge['velocity_ms'],
           color='none', marker='o', s=420, zorder=7,
           edgecolors='#e07b00', linewidths=2.0)

ax.annotate('haz=0.22\nall 3 thresholds miss',
            xy=(0.15, 1.5), xytext=(0.07, 2.15),
            fontsize=8, color='#7d4000', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#b05900', lw=1.0), zorder=9)

ax.annotate('haz=0.45\n4WD threshold misses',
            xy=(0.30, 1.5), xytext=(0.30, 2.15),
            fontsize=8, color='#7d4000', fontweight='bold', ha='center',
            arrowprops=dict(arrowstyle='->', color='#b05900', lw=1.0), zorder=9)

ax.annotate('haz=0.30\n4WD + large pass miss',
            xy=(0.30, 1.0), xytext=(0.42, 0.62),
            fontsize=8, color='#7d4000', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#b05900', lw=1.0), zorder=9)

ax.text(0.60, 0.42,
        'L2 detects persistent lateral drag\nthat no D\u00d7V threshold can represent.\nStructural failure, not a calibration issue.',
        fontsize=8.5, color='#333333', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.50', facecolor='#fff8e6',
                  edgecolor='#e07b00', alpha=0.96),
        zorder=10)

ax.set_xlabel('Water Depth (m)', fontsize=12)
ax.set_ylabel('Flow Velocity (m/s)', fontsize=12)
ax.set_title('Can It Ford? -- L2 (Genesis SPH Pilot) Phase Space vs L1 (AR&R) Predictions',
             fontsize=12, fontweight='bold')
ax.set_xlim(0.05, 0.75)
ax.set_ylim(-0.10, 2.95)

ax.legend(fontsize=9, bbox_to_anchor=(1.01, 1), loc='upper left',
          framealpha=0.93, edgecolor='#cccccc', borderaxespad=0)
ax.grid(True, alpha=0.20, color='gray')

plt.tight_layout()
plt.savefig('can_it_ford_phase_space_v2.png', dpi=150, bbox_inches='tight')
print('Saved: can_it_ford_phase_space_v2.png')
