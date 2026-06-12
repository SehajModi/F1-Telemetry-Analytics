import numpy as np
import matplotlib.pyplot as plt
import os
from f1_telemetry.config import COLORS, OUTPUT_DIR


def compute_time_delta(tel_a, tel_b):
    dist_min = max(tel_a["Distance"].min(), tel_b["Distance"].min())
    dist_max = min(tel_a["Distance"].max(), tel_b["Distance"].max())
    common_dist = np.linspace(dist_min, dist_max, 1000)

    time_a = np.interp(common_dist, tel_a["Distance"], tel_a["Time"].dt.total_seconds())
    time_b = np.interp(common_dist, tel_b["Distance"], tel_b["Time"].dt.total_seconds())

    delta = time_b - time_a  # positive = driver A is faster
    return common_dist, delta


def plot_telemetry_comparison(lap_a, lap_b, driver_a: str, driver_b: str, save: bool = True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tel_a = lap_a.get_telemetry().add_distance()
    tel_b = lap_b.get_telemetry().add_distance()

    common_dist, delta = compute_time_delta(tel_a, tel_b)

    fig, axes = plt.subplots(5, 1, figsize=(16, 18),
                             facecolor=COLORS["background"],
                             gridspec_kw={"height_ratios": [2, 1, 1, 1, 1.5]})
    fig.suptitle(f"{driver_a} vs {driver_b} — Bahrain GP 2025 Qualifying",
                 color=COLORS["text"], fontsize=15, fontweight="bold", y=0.98)

    color_a = COLORS["accent"]
    color_b = COLORS["gold"]

    channels = [
        ("Speed", "Speed (km/h)"),
        ("Throttle", "Throttle (%)"),
        ("Brake", "Brake"),
        ("nGear", "Gear"),
    ]

    for ax, (channel, ylabel) in zip(axes[:4], channels):
        ax.set_facecolor(COLORS["panel"])
        ax.plot(tel_a["Distance"], tel_a[channel],
                color=color_a, linewidth=1.2, label=driver_a)
        ax.plot(tel_b["Distance"], tel_b[channel],
                color=color_b, linewidth=1.2, label=driver_b, alpha=0.85)
        ax.set_ylabel(ylabel, color=COLORS["text"], fontsize=9)
        ax.tick_params(colors=COLORS["text"], labelsize=8)
        ax.legend(facecolor=COLORS["background"], labelcolor=COLORS["text"],
                  fontsize=8, loc="upper right")
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["spine"])
        ax.set_xlim(0, tel_a["Distance"].max())

    # Time delta panel
    ax_delta = axes[4]
    ax_delta.set_facecolor(COLORS["panel"])
    ax_delta.axhline(0, color=COLORS["grey"], linewidth=0.8, linestyle="--")
    ax_delta.fill_between(common_dist, delta, 0,
                          where=(delta > 0), color=color_a, alpha=0.3,
                          label=f"{driver_a} faster")
    ax_delta.fill_between(common_dist, delta, 0,
                          where=(delta < 0), color=color_b, alpha=0.3,
                          label=f"{driver_b} faster")
    ax_delta.plot(common_dist, delta, color=COLORS["text"], linewidth=1.0)
    ax_delta.set_ylabel("Time Delta (s)", color=COLORS["text"], fontsize=9)
    ax_delta.set_xlabel("Distance (m)", color=COLORS["text"], fontsize=10)
    ax_delta.tick_params(colors=COLORS["text"], labelsize=8)
    ax_delta.legend(facecolor=COLORS["background"], labelcolor=COLORS["text"], fontsize=8)
    for spine in ax_delta.spines.values():
        spine.set_edgecolor(COLORS["spine"])
    ax_delta.set_xlim(0, common_dist.max())

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, f"{driver_a.lower()}_{driver_b.lower()}_delta.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["background"])
        print(f"Saved → {path}")

    plt.show()