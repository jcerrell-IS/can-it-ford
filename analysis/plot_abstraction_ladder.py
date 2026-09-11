import matplotlib.pyplot as plt

depths_l0 = [0.15, 0.20, 0.30, 0.45, 0.60, 0.80]
l0_verdict = [0, 0, 0, 0, 0, 0]

depths_l1 = [0.15, 0.20, 0.30, 0.45, 0.60, 0.80]
l1_verdict_v15 = [1, 1, 1, 1, 0, 1]

depths_l2_still = [0.15, 0.30, 0.45, 0.60, 0.80]
l2_still = [1, 1, 1, 1, 1]

l2_open_depth = [0.30]
l2_open_verdict = [0]

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(depths_l0, l0_verdict, 'bs-', markersize=9, linewidth=1.8, label='L0: Static Depth Threshold')
ax.plot(depths_l1, l1_verdict_v15, 'g^--', markersize=9, linewidth=1.8, label='L1: AR&R Depth-Velocity (v=1.5 m/s)')
ax.plot(depths_l2_still, l2_still, 'ro-', markersize=9, linewidth=1.8, label='L2: Genesis SPH Pilot (still water)')
ax.scatter(l2_open_depth, l2_open_verdict, color='darkred', s=160, marker='X', zorder=6,
           label='L2: Genesis SPH Pilot (open-channel, v=1.5 m/s) -- KEY RESULT')
ax.axvline(0.30, color='gray', linestyle='--', linewidth=1.8,
           label='NWS 12in / Smith-Modra-Felder sedan threshold')
ax.axvline(0.60, color='dimgray', linestyle=':', linewidth=1.2, label='NWS 24in threshold')
ax.set_xlabel('Water Depth (m)', fontsize=13)
ax.set_ylabel('Verdict  (1=FORD,  0=NO-FORD)', fontsize=13)
ax.set_title('Can It Ford?  Abstraction Ladder Comparison\nL2 open-channel detects danger L1 misses at 0.30m / 1.5m/s',
             fontsize=12)
ax.set_ylim(-0.3, 1.5)
ax.set_xlim(0.05, 0.90)
ax.legend(fontsize=8.5, loc='upper right')
ax.set_yticks([0, 1])
ax.set_yticklabels(['NO-FORD', 'FORD'], fontsize=11)
plt.tight_layout()
plt.savefig('can_it_ford_validation.png', dpi=200)
print("Saved: can_it_ford_validation.png")
