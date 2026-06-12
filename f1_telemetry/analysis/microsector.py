import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
from f1_telemetry.config import COLORS, OUTPUT_DIR


def compute_microsector_dominance(tel_a, tel_b, segment_size_m: float = 50.0):
    """
    Split the lap into segments of segment_size_m meters.
    For each segment, compare average speed of driver A vs B.
    Returns a DataFrame with dominance per segment.
    """
    dist_min = max(tel_a["Distance"].min(), tel_b["Distance"].min())
    dist_max = min(tel_a["Distance"].max(), tel_b["Distance"].max())

    bins = np.arange(dist_min, dist_max, segment_size_m)
    records = []

    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]

        seg_a = tel_a[(tel_a["Distance"] >= lo) & (tel_a["Distance"] < hi)]
        seg_b = tel_b[(tel_b["Distance"] >= lo) & (tel_b["Distance"] < hi)]

        if seg_a.empty or seg_b.empty:
            continue

        avg_speed_a = seg_a["Speed"].mean()
        avg_speed_b = seg_b["Speed"].mean()
        delta = avg_speed_a - avg_speed_b  # positive = A faster

        records.append({
            "segment_start": round(lo, 1),
            "segment_mid": round((lo + hi) / 2, 1),
            "avg_speed_a": round(avg_speed_a, 2),
            "avg_speed_b": round(avg_speed_b, 2),
            "speed_delta": round(delta, 2),
            "dominant": "A" if delta > 0 else "B",
        })

    return pd.DataFrame(records)


def plot_microsector_dominance(dom_df, driver_a: str, driver_b: str, save: bool = True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    color_a = COLORS["accent"]
    color_b = COLORS["gold"]

    fig, axes = plt.subplots(2, 1, figsize=(18, 8),
                             facecolor=COLORS["background"],
                             gridspec_kw={"height_ratios": [1, 2]})
    fig.suptitle(f"Micro-Sector Dominance — {driver_a} vs {driver_b}\nBahrain GP 2025 Qualifying (50m segments)",
                 color=COLORS["text"], fontsize=14, fontweight="bold", y=1.01)

    # Top: dominance strip
    ax_strip = axes[0]
    ax_strip.set_facecolor(COLORS["panel"])
    ax_strip.set_xlim(dom_df["segment_start"].min(), dom_df["segment_start"].max())
    ax_strip.set_ylim(0, 1)
    ax_strip.set_yticks([])
    ax_strip.set_ylabel("Dominance", color=COLORS["text"], fontsize=9)
    ax_strip.tick_params(colors=COLORS["text"], labelsize=8)

    for _, row in dom_df.iterrows():
        color = color_a if row["dominant"] == "A" else color_b
        ax_strip.axvspan(row["segment_start"],
                         row["segment_start"] + 50,
                         color=color, alpha=0.85)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_a, label=f"{driver_a} faster"),
        Patch(facecolor=color_b, label=f"{driver_b} faster"),
    ]
    ax_strip.legend(handles=legend_elements,
                    facecolor=COLORS["background"],
                    labelcolor=COLORS["text"], fontsize=9, loc="upper right")
    for spine in ax_strip.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    # Bottom: speed delta bar chart
    ax_delta = axes[1]
    ax_delta.set_facecolor(COLORS["panel"])
    ax_delta.axhline(0, color=COLORS["grey"], linewidth=0.8, linestyle="--")

    colors = [color_a if v > 0 else color_b for v in dom_df["speed_delta"]]
    ax_delta.bar(dom_df["segment_mid"], dom_df["speed_delta"],
                 width=45, color=colors, alpha=0.85)

    ax_delta.set_xlabel("Distance (m)", color=COLORS["text"], fontsize=10)
    ax_delta.set_ylabel(f"Avg Speed Delta\n{driver_a} – {driver_b} (kph)",
                        color=COLORS["text"], fontsize=9)
    ax_delta.tick_params(colors=COLORS["text"], labelsize=8)
    for spine in ax_delta.spines.values():
        spine.set_edgecolor(COLORS["spine"])

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, f"{driver_a.lower()}_{driver_b.lower()}_microsector.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["background"])
        print(f"Saved → {path}")

    plt.show()


def print_dominance_summary(dom_df, driver_a: str, driver_b: str):
    total = len(dom_df)
    a_count = (dom_df["dominant"] == "A").sum()
    b_count = (dom_df["dominant"] == "B").sum()

    print(f"\n--- Micro-Sector Dominance Summary ---")
    print(f"Total segments (50m): {total}")
    print(f"{driver_a} faster in: {a_count} segments ({100*a_count/total:.1f}%)")
    print(f"{driver_b} faster in: {b_count} segments ({100*b_count/total:.1f}%)")
    print(f"Max {driver_a} advantage: +{dom_df['speed_delta'].max():.2f} kph")
    print(f"Max {driver_b} advantage: {dom_df['speed_delta'].min():.2f} kph")