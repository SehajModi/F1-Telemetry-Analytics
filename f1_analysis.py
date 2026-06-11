import fastf1
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

fastf1.Cache.enable_cache('f1_cache')

session = fastf1.get_session(2025, 'Bahrain', 'Q')
session.load()

ver = session.laps.pick_drivers('VER').pick_fastest()
nor = session.laps.pick_drivers('NOR').pick_fastest()

ver_tel = ver.get_telemetry().add_distance()
nor_tel = nor.get_telemetry().add_distance()

# Interpolate NOR onto VER's distance axis
from scipy.interpolate import interp1d

ver_dist = ver_tel['Distance'].values
nor_dist = nor_tel['Distance'].values
nor_time = nor_tel['SessionTime'].dt.total_seconds().values
ver_time = ver_tel['SessionTime'].dt.total_seconds().values

# Interpolate
nor_interp = interp1d(nor_dist, nor_time, bounds_error=False, fill_value='extrapolate')
nor_time_on_ver = nor_interp(ver_dist)

# Delta: positive = VER ahead, negative = NOR ahead
delta = ver_time - nor_time_on_ver
# Normalize to 0 at start
delta = delta - delta[0]

ver_speed = ver_tel['Speed'].values

# Plot
fig = plt.figure(figsize=(16, 8), facecolor='#1a1a2e')
fig.suptitle("VER vs NOR — Bahrain GP 2025 Q\nTime Delta & Speed Trace",
             color='white', fontsize=15, fontweight='bold')

gs = gridspec.GridSpec(2, 1, hspace=0.15, height_ratios=[1, 2])

# Delta plot
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor('#0d0d1a')
ax1.axhline(0, color='white', linewidth=0.6, linestyle='--', alpha=0.4)
ax1.fill_between(ver_dist, delta, 0,
                 where=(delta > 0), color='#1E90FF', alpha=0.7, label='VER faster')
ax1.fill_between(ver_dist, delta, 0,
                 where=(delta < 0), color='#FF8C00', alpha=0.7, label='NOR faster')
ax1.set_ylabel('Delta (s)', color='white', fontsize=9)
ax1.tick_params(colors='white')
ax1.legend(facecolor='#1a1a2e', labelcolor='white', fontsize=9, loc='upper right')
ax1.set_xticklabels([])
for spine in ax1.spines.values():
    spine.set_edgecolor('#333355')

# Speed trace
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('#0d0d1a')
ax2.plot(ver_dist, ver_speed, color='#1E90FF', linewidth=1.2, label='VER Speed')
ax2.set_ylabel('Speed (km/h)', color='white', fontsize=9)
ax2.set_xlabel('Distance (m)', color='white', fontsize=10)
ax2.tick_params(colors='white')
ax2.legend(facecolor='#1a1a2e', labelcolor='white', fontsize=9)
for spine in ax2.spines.values():
    spine.set_edgecolor('#333355')

plt.savefig('ver_nor_delta.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
print("Saved!")
plt.show()