import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from f1_telemetry.config import COLORS, OUTPUT_DIR


def extract_braking_zones(tel, min_duration_m: float = 30.0):
    """
    Detect braking events from telemetry.
    A braking event = Brake > 0.5 sustained for at least min_duration_m meters.
    Returns a DataFrame with one row per braking zone.
    """
    brake = tel["Brake"].values
    dist = tel["Distance"].values
    speed = tel["Speed"].values

    braking = brake > 0.5
    zones = []
    in_zone = False
    start_idx = 0

    for i in range(len(braking)):
        if braking[i] and not in_zone:
            in_zone = True
            start_idx = i
        elif not braking[i] and in_zone:
            in_zone = False
            end_idx = i - 1
            zone_dist = dist[end_idx] - dist[start_idx]
            if zone_dist >= min_duration_m:
                zones.append({
                    "zone": len(zones) + 1,
                    "start_dist_m": round(dist[start_idx], 1),
                    "end_dist_m": round(dist[end_idx], 1),
                    "braking_distance_m": round(zone_dist, 1),
                    "entry_speed_kph": round(speed[start_idx], 1),
                    "exit_speed_kph": round(speed[end_idx], 1),
                    "speed_scrubbed_kph": round(speed[start_idx] - speed[end_idx], 1),
                    "peak_decel_proxy": round((speed[start_idx] - speed[end_idx]) / zone_dist, 4),
                })

    return pd.DataFrame(zones)


def plot_braking_zones(tel, zones_df, driver: str, save: bool = True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(16, 10),
                             facecolor=COLORS["background"],
                             gridspec_kw={"height_ratios": [2, 1, 1]})
    fig.suptitle(f"{driver} — Braking Zone Analysis\nBahrain GP 2025 Qualifying",
                 color=COLORS["text"], fontsize=14, fontweight="bold", y=0.98)

    # Speed trace with braking zones highlighted
    ax1 = axes[0]
    ax1.set_facecolor(COLORS["panel"])
    ax1.plot(tel["Distance"], tel["Speed"],
             color=COLORS["accent"], linewidth=1.5, label="Speed")

    for _, zone in zones_df.iterrows():
        ax1.axvspan(zone["start_dist_m"], zone["end_dist_m"],
                    color="#ff4444", alpha=0.25)
        ax1.text(zone["start_dist_m"] + (zone["braking_distance_m"] / 2),
                 tel["Speed"].max() * 0.92,
                 f"Z{int(zone['zone'])}", color="#ff4444",
                 fontsize=7, ha="center", fontweight="bold")

    ax1.set_ylabel("Speed (km/h)", color=COLORS["text"], fontsize=9)
    ax1.tick_params(colors=COLORS["text"], labelsize=8)
    ax1.legend(facecolor=COLORS["background"], labelcolor=COLORS["text"], fontsize=8)
    for spine in ax1.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    # Brake trace
    ax2 = axes[1]
    ax2.set_facecolor(COLORS["panel"])
    ax2.fill_between(tel["Distance"], tel["Brake"],
                     color="#ff4444", alpha=0.6, label="Brake")
    ax2.set_ylabel("Brake", color=COLORS["text"], fontsize=9)
    ax2.tick_params(colors=COLORS["text"], labelsize=8)
    ax2.legend(facecolor=COLORS["background"], labelcolor=COLORS["text"], fontsize=8)
    for spine in ax2.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    # Braking distance per zone bar chart
    ax3 = axes[2]
    ax3.set_facecolor(COLORS["panel"])
    bars = ax3.bar(zones_df["zone"].astype(str),
                   zones_df["braking_distance_m"],
                   color=COLORS["accent"], alpha=0.8, edgecolor=COLORS["spine"])

    for bar, (_, row) in zip(bars, zones_df.iterrows()):
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 1,
                 f"{row['entry_speed_kph']:.0f}→{row['exit_speed_kph']:.0f}",
                 color=COLORS["text"], fontsize=6.5, ha="center")

    ax3.set_xlabel("Braking Zone", color=COLORS["text"], fontsize=9)
    ax3.set_ylabel("Braking Distance (m)", color=COLORS["text"], fontsize=9)
    ax3.tick_params(colors=COLORS["text"], labelsize=8)
    for spine in ax3.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, f"{driver.lower()}_braking_zones.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["background"])
        print(f"Saved → {path}")

    plt.show()
    return zones_df