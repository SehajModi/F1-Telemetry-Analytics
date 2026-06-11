import fastf1
import matplotlib.pyplot as plt
import numpy as np

fastf1.Cache.enable_cache('f1_cache')

session = fastf1.get_session(2025, 'Bahrain', 'Q')
session.load()

ver_laps = session.laps.pick_drivers('VER').pick_quicklaps()
ver_laps = ver_laps.copy()
ver_laps['LapTimeSeconds'] = ver_laps['LapTime'].dt.total_seconds()

q1 = ver_laps[ver_laps['Session'] == 'Q1'] if 'Session' in ver_laps.columns else ver_laps[ver_laps['LapNumber'] <= 12]

fig, ax = plt.subplots(figsize=(14, 7), facecolor='#1a1a2e')
ax.set_facecolor('#0d0d1a')
ax.set_title("Max Verstappen — Bahrain GP 2025\nQualifying Lap Time Evolution",
             color='white', fontsize=14, fontweight='bold')

colors = {'Q1': '#888888', 'Q2': '#00d2ff', 'Q3': '#ffd700'}

for i, (compound_color, lap) in enumerate(zip(
    ['#aaaaaa'] * len(ver_laps), ver_laps.itertuples()
)):
    pass

# Simple approach - plot all laps in order
lap_nums = range(1, len(ver_laps) + 1)
lap_times = ver_laps['LapTimeSeconds'].values
best = min(lap_times)

ax.plot(lap_nums, lap_times, color='#00d2ff', linewidth=2, marker='o',
        markersize=6, markerfacecolor='white', markeredgecolor='#00d2ff')

# Highlight fastest lap
fastest_idx = np.argmin(lap_times)
ax.scatter(fastest_idx + 1, lap_times[fastest_idx], color='#ffd700',
           s=150, zorder=5, label=f'Fastest: {best:.3f}s')

# Annotate each point
for i, t in enumerate(lap_times):
    ax.annotate(f'{t:.2f}s', (i+1, t), textcoords='offset points',
                xytext=(0, 10), color='white', fontsize=7, ha='center')

ax.set_xlabel('Lap Number', color='white', fontsize=11)
ax.set_ylabel('Lap Time (seconds)', color='white', fontsize=11)
ax.tick_params(colors='white')
ax.legend(facecolor='#1a1a2e', labelcolor='white', fontsize=10)
for spine in ax.spines.values():
    spine.set_edgecolor('#333355')

plt.tight_layout()
plt.savefig('ver_lap_evolution.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
print("Saved!")
plt.show()