"""
tyre_deg.py
-----------
Tyre degradation: lap time vs lap number coloured by compound.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os

YEAR   = 2025
GP     = "Bahrain"
TOP_N  = 5

COMPOUND_COLORS = {
    "SOFT":   "#FF3333",
    "MEDIUM": "#FFD700",
    "HARD":   "#E0E0E0",
    "INTER":  "#39B54A",
    "WET":    "#0066CC",
}

os.makedirs("f1_cache", exist_ok=True)
os.makedirs("outputs",  exist_ok=True)

fastf1.Cache.enable_cache("f1_cache")
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")

session = fastf1.get_session(YEAR, GP, "R")
session.load()

laps = session.laps.copy()
laps = laps[laps['PitOutTime'].isna() & laps['PitInTime'].isna()]
laps = laps[laps['LapTime'].notna()]
laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()

median_t = laps['LapTimeSec'].median()
laps = laps[(laps['LapTimeSec'] < median_t * 1.07) & (laps['LapTimeSec'] > median_t * 0.96)]

results = session.results.sort_values('Position').head(TOP_N)
top_drivers = results['Abbreviation'].tolist()

fig, ax = plt.subplots(figsize=(15, 7))
fig.patch.set_facecolor('#0F0F0F')
ax.set_facecolor('#0F0F0F')
ax.tick_params(colors='#AAAAAA')
ax.spines[:].set_color('#333333')

compound_seen = set()

for driver in top_drivers:
    drv_laps = laps[laps['Driver'] == driver].sort_values('LapNumber')
    if drv_laps.empty:
        continue
    d_color = fastf1.plotting.get_driver_color(driver, session)
    drv_laps = drv_laps.copy()
    drv_laps['StintNum'] = (drv_laps['Compound'] != drv_laps['Compound'].shift()).cumsum()

    for stint_id, stint in drv_laps.groupby('StintNum'):
        compound = str(stint['Compound'].iloc[0]).upper()
        c_color  = COMPOUND_COLORS.get(compound, '#FFFFFF')
        compound_seen.add(compound)
        lap_nums  = stint['LapNumber'].values
        lap_times = stint['LapTimeSec'].values

        ax.scatter(lap_nums, lap_times, color=c_color, s=22, alpha=0.55, zorder=2, linewidths=0)

        if len(lap_times) >= 3:
            roll = pd.Series(lap_times).rolling(3, center=True, min_periods=2).mean().values
            ax.plot(lap_nums, roll, color=d_color, linewidth=1.6, alpha=0.85, zorder=3)

        ax.annotate(f"{driver}\n{compound[0]}", xy=(lap_nums[0], lap_times[0]),
                    xytext=(-4, -12), textcoords='offset points',
                    color=d_color, fontsize=7, ha='center', fontweight='bold')

    pit_laps_raw = session.laps[session.laps['Driver'] == driver]
    pit_in_laps = pit_laps_raw[pit_laps_raw['PitInTime'].notna()]['LapNumber'].values
    for pl in pit_in_laps:
        ax.axvline(pl, color=d_color, linewidth=0.8, linestyle=':', alpha=0.4, zorder=1)

comp_patches = [mpatches.Patch(color=COMPOUND_COLORS[c], label=c)
                for c in ["SOFT","MEDIUM","HARD","INTER","WET"] if c in compound_seen]
leg = ax.legend(handles=comp_patches, title="Compound", loc='upper right',
                facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white', title_fontsize=8)
leg.get_title().set_color('#AAAAAA')

driver_patches = [mpatches.Patch(color=fastf1.plotting.get_driver_color(d, session), label=d)
                  for d in top_drivers if not laps[laps['Driver'] == d].empty]
leg2 = ax.legend(handles=driver_patches, title="Driver", loc='upper left',
                  facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white', title_fontsize=8)
leg2.get_title().set_color('#AAAAAA')
ax.add_artist(leg)

def fmt_laptime(x, _):
    m = int(x // 60)
    s = x % 60
    return f"{m}:{s:05.2f}"

ax.yaxis.set_major_formatter(plt.FuncFormatter(fmt_laptime))
ax.set_xlabel("Lap Number", fontsize=11, color='#CCCCCC')
ax.set_ylabel("Lap Time", fontsize=11, color='#CCCCCC')
ax.set_title(f"{YEAR} {GP} GP — Tyre Degradation by Stint (Top {TOP_N} Finishers)",
             color='white', fontsize=14, fontweight='bold', pad=14)
ax.grid(color='#1E1E1E', linewidth=0.6, zorder=0)
ax.annotate("Dotted vertical lines = pit stops per driver",
            xy=(0.01, 0.02), xycoords='axes fraction', color='#666666', fontsize=8)

plt.tight_layout()
plt.savefig("outputs/tyre_deg.png", dpi=150, bbox_inches='tight', facecolor='#0F0F0F')
print("✅ Saved: outputs/tyre_deg.png")
plt.show()