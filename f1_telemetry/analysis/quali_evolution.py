"""
quali_evolution.py
------------------
Qualifying lap time evolution: Q1 → Q2 → Q3 for top drivers.
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

YEAR   = 2025
GP     = "Bahrain"
TOP_N  = 6

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

session = fastf1.get_session(YEAR, GP, "Q")
session.load()

laps = session.laps.copy()
laps = laps[laps['LapTime'].notna()]
laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()

def assign_segment(row):
    if pd.isna(row['Time']):
        return None
    t = row['Time'].total_seconds()
    if t < 18 * 60:
        return "Q1"
    elif t < 37 * 60:
        return "Q2"
    else:
        return "Q3"

laps['Segment'] = laps.apply(assign_segment, axis=1)
laps = laps[laps['Segment'].notna()]

best = (laps.groupby(['Driver', 'Segment'])
        .apply(lambda x: x.loc[x['LapTimeSec'].idxmin()])
        .reset_index(drop=True))

q3_best = best[best['Segment'] == 'Q3'].sort_values('LapTimeSec').head(TOP_N)
top_drivers = q3_best['Driver'].tolist()

if len(top_drivers) < TOP_N:
    q2_best = best[best['Segment'] == 'Q2'].sort_values('LapTimeSec')
    extra = [d for d in q2_best['Driver'] if d not in top_drivers]
    top_drivers += extra[:TOP_N - len(top_drivers)]

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor('#0F0F0F')
ax.set_facecolor('#0F0F0F')
ax.tick_params(colors='#AAAAAA')
ax.spines[:].set_color('#333333')

segments = ["Q1", "Q2", "Q3"]
seg_x    = {s: i for i, s in enumerate(segments)}
ref_time = best[best['Driver'].isin(top_drivers)]['LapTimeSec'].min()

for driver in top_drivers:
    drv_data = best[best['Driver'] == driver].sort_values('Segment')
    d_color  = fastf1.plotting.get_driver_color(driver, session)
    xs, ys, compounds = [], [], []
    for _, row in drv_data.iterrows():
        if row['Segment'] in seg_x:
            xs.append(seg_x[row['Segment']])
            ys.append(row['LapTimeSec'] - ref_time)
            compounds.append(row.get('Compound', 'SOFT'))
    if len(xs) < 2:
        continue
    ax.plot(xs, ys, color=d_color, linewidth=2.0, alpha=0.9, zorder=2)
    for x, y, comp in zip(xs, ys, compounds):
        c_color = COMPOUND_COLORS.get(str(comp).upper(), '#FFFFFF')
        ax.scatter(x, y, color=c_color, edgecolors=d_color, s=110, linewidths=2.0, zorder=3)
    ax.annotate(driver, xy=(xs[-1], ys[-1]),
                xytext=(8, 0), textcoords='offset points',
                color=d_color, fontsize=9, fontweight='bold', va='center')

ax.axhline(0, color='#FFDD00', linewidth=0.8, linestyle='--', alpha=0.6, label='Pole reference')

comp_patches = [mpatches.Patch(color=v, label=k)
                for k, v in COMPOUND_COLORS.items()
                if k in best['Compound'].str.upper().values]
legend1 = ax.legend(handles=comp_patches, title="Compound", loc='upper right',
                     facecolor='#1A1A1A', edgecolor='#444444', labelcolor='white', title_fontsize=8)
legend1.get_title().set_color('#AAAAAA')
ax.add_artist(legend1)

ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["Q1", "Q2", "Q3"], fontsize=12, color='white', fontweight='bold')
ax.set_xlim(-0.3, 2.6)

def fmt_delta(x, _):
    return f"+{x:.2f}s" if x >= 0 else f"{x:.2f}s"
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_delta))
ax.set_ylabel("Gap to Pole (s)", fontsize=11, color='#CCCCCC')
ax.set_title(f"{YEAR} {GP} GP — Qualifying Lap Evolution (Top {TOP_N})",
             color='white', fontsize=14, fontweight='bold', pad=14)

for i, col in enumerate(['#1A1A2E', '#0F0F1A', '#1A1A2E']):
    ax.axvspan(i - 0.4, i + 0.4, color=col, alpha=0.5, zorder=0)

ax.grid(axis='y', color='#2A2A2A', linewidth=0.6)
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("outputs/quali_evolution.png", dpi=150, bbox_inches='tight', facecolor='#0F0F0F')
print("✅ Saved: outputs/quali_evolution.png")
plt.show()