"""
sector_delta.py
---------------
Sector-by-sector time delta between two drivers in qualifying.
Shows exactly where on track time is gained or lost.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import os

YEAR     = 2025
GP       = "Bahrain"
SESSION  = "Q"
DRIVER_1 = "VER"
DRIVER_2 = "NOR"

os.makedirs("f1_cache", exist_ok=True)
os.makedirs("outputs",  exist_ok=True)

fastf1.Cache.enable_cache("f1_cache")
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")

session = fastf1.get_session(YEAR, GP, SESSION)
session.load()

lap1 = session.laps.pick_driver(DRIVER_1).pick_fastest()
lap2 = session.laps.pick_driver(DRIVER_2).pick_fastest()

tel1 = lap1.get_telemetry().add_distance()
tel2 = lap2.get_telemetry().add_distance()

def sector_distance(lap, tel, sector_col):
    split_time = lap[sector_col]
    if hasattr(split_time, 'total_seconds'):
        split_sec = split_time.total_seconds()
    else:
        split_sec = float(split_time)
    idx = (tel['Time'].dt.total_seconds() - split_sec).abs().idxmin()
    return tel.loc[idx, 'Distance']

s1_dist = sector_distance(lap1, tel1, 'Sector1Time')
s2_dist = sector_distance(lap1, tel1, 'Sector2Time')

common_dist = np.linspace(0, min(tel1['Distance'].max(), tel2['Distance'].max()), 1500)
speed1 = np.interp(common_dist, tel1['Distance'].values, tel1['Speed'].values)
speed2 = np.interp(common_dist, tel2['Distance'].values, tel2['Speed'].values)
delta_speed = speed1 - speed2

avg_speed = np.where((speed1 + speed2) / 2 < 1, 1, (speed1 + speed2) / 2)
dx = np.diff(common_dist, prepend=common_dist[0])
cumulative_delta = np.cumsum(-dx / (avg_speed * (1000/3600)) * delta_speed / avg_speed)

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                          gridspec_kw={'height_ratios': [2, 2, 1]})
fig.patch.set_facecolor('#0F0F0F')
for ax in axes:
    ax.set_facecolor('#0F0F0F')
    ax.tick_params(colors='#AAAAAA')
    ax.spines[:].set_color('#333333')
    ax.yaxis.label.set_color('#CCCCCC')

d1_color = fastf1.plotting.get_driver_color(DRIVER_1, session)
d2_color = fastf1.plotting.get_driver_color(DRIVER_2, session)

axes[0].plot(common_dist, speed1, color=d1_color, linewidth=1.4, label=DRIVER_1)
axes[0].plot(common_dist, speed2, color=d2_color, linewidth=1.4, label=DRIVER_2, alpha=0.85)
axes[0].set_ylabel("Speed (km/h)", fontsize=10)
axes[0].legend(loc="upper right", facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white')
axes[0].set_title(f"{YEAR} {GP} GP — Qualifying Sector Delta: {DRIVER_1} vs {DRIVER_2}",
                   color='white', fontsize=13, fontweight='bold', pad=12)

axes[1].fill_between(common_dist, delta_speed, 0,
                      where=delta_speed >= 0, color=d1_color, alpha=0.55, label=f"{DRIVER_1} faster")
axes[1].fill_between(common_dist, delta_speed, 0,
                      where=delta_speed < 0,  color=d2_color, alpha=0.55, label=f"{DRIVER_2} faster")
axes[1].axhline(0, color='#555555', linewidth=0.8, linestyle='--')
axes[1].set_ylabel("Speed Δ (km/h)", fontsize=10)
axes[1].legend(loc="upper right", facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white')

for ax in axes:
    ax.axvline(s1_dist, color='#FFDD00', linewidth=1.0, linestyle=':', alpha=0.7)
    ax.axvline(s2_dist, color='#FFDD00', linewidth=1.0, linestyle=':', alpha=0.7)

axes[2].plot(common_dist, cumulative_delta, color='#FFFFFF', linewidth=1.4)
axes[2].fill_between(common_dist, cumulative_delta, 0,
                      where=cumulative_delta >= 0, color=d1_color, alpha=0.3)
axes[2].fill_between(common_dist, cumulative_delta, 0,
                      where=cumulative_delta < 0,  color=d2_color, alpha=0.3)
axes[2].axhline(0, color='#555555', linewidth=0.8, linestyle='--')
axes[2].set_ylabel("Cumul. Δ (s)", fontsize=10)
axes[2].set_xlabel("Distance (m)", fontsize=10, color='#AAAAAA')

for x, label in [(s1_dist/2, "S1"), ((s1_dist+s2_dist)/2, "S2"),
                  ((s2_dist+common_dist[-1])/2, "S3")]:
    axes[2].text(x, axes[2].get_ylim()[0]*0.85, label,
                 color='#FFDD00', fontsize=9, ha='center', fontweight='bold')

t1 = lap1['LapTime']
t2 = lap2['LapTime']
gap = (t2 - t1).total_seconds()
gap_str = f"+{gap:.3f}s" if gap > 0 else f"{gap:.3f}s"
axes[0].annotate(
    f"{DRIVER_1}: {str(t1)[10:19]}   {DRIVER_2}: {str(t2)[10:19]}  ({gap_str})",
    xy=(0.02, 0.07), xycoords='axes fraction',
    color='#CCCCCC', fontsize=9,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1A1A1A', edgecolor='#444444')
)

plt.tight_layout(h_pad=0.4)
plt.savefig("outputs/sector_delta.png", dpi=150, bbox_inches='tight', facecolor='#0F0F0F')
print("✅ Saved: outputs/sector_delta.png")
plt.show()