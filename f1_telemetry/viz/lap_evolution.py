import matplotlib.pyplot as plt
import numpy as np
import os
from f1_telemetry.config import COLORS, OUTPUT_DIR


def plot_lap_evolution(laps, driver: str, save: bool = True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lap_nums = range(1, len(laps) + 1)
    lap_times = laps["LapTimeSeconds"].values
    best = min(lap_times)
    fastest_idx = int(np.argmin(lap_times))

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORS["background"])
    ax.set_facecolor(COLORS["panel"])

    ax.plot(lap_nums, lap_times,
            color=COLORS["accent"], linewidth=2,
            marker="o", markersize=6,
            markerfacecolor="white", markeredgecolor=COLORS["accent"])

    ax.scatter(fastest_idx + 1, lap_times[fastest_idx],
               color=COLORS["gold"], s=150, zorder=5,
               label=f"Fastest: {best:.3f}s")

    for i, t in enumerate(lap_times):
        ax.annotate(f"{t:.2f}s", (i + 1, t),
                    textcoords="offset points", xytext=(0, 10),
                    color=COLORS["text"], fontsize=7, ha="center")

    ax.set_title(f"{driver} — Bahrain GP 2025\nQualifying Lap Time Evolution",
                 color=COLORS["text"], fontsize=14, fontweight="bold")
    ax.set_xlabel("Lap Number", color=COLORS["text"], fontsize=11)
    ax.set_ylabel("Lap Time (seconds)", color=COLORS["text"], fontsize=11)
    ax.tick_params(colors=COLORS["text"])
    ax.legend(facecolor=COLORS["background"], labelcolor=COLORS["text"], fontsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, f"{driver.lower()}_lap_evolution.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["background"])
        print(f"Saved → {path}")

    plt.show()