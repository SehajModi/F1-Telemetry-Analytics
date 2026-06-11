import fastf1
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

fastf1.Cache.enable_cache('f1_cache')

session = fastf1.get_session(2025, 'Bahrain', 'Q')
session.load()

ver = session.laps.pick_drivers('VER').pick_fastest()
nor = session.laps.pick_drivers('NOR').pick_fastest()

ver_tel = ver.get_telemetry()
nor_tel = nor.get_telemetry()

fig = plt.figure(figsize=(16, 10), facecolor='#1a1a2e')
fig.suptitle("VER vs NOR — Bahrain GP 2025 Qualifying\nTelemetry Comparison",
             color='white', fontsize=16, fontweight='bold')

gs = gridspec.GridSpec(3, 1, hspace=0.4)
axes = [fig.add_subplot(gs[i]) for i in range(3)]

channels = [
    ('Speed',    'Speed (km/h)'),
    ('Throttle', 'Throttle (%)'),
    ('Brake',    'Brake'),
]

for ax, (col, ylabel) in zip(axes, channels):
    ax.set_facecolor('#0d0d1a')
    ax.plot(ver_tel['Distance'], ver_tel[col], color='#1E90FF', linewidth=1.2, label='VER')
    ax.plot(nor_tel['Distance'], nor_tel[col], color='#FF8C00', linewidth=1.2, label='NOR', alpha=0.85)
    ax.set_ylabel(ylabel, color='white', fontsize=9)
    ax.tick_params(colors='white')
    ax.legend(facecolor='#1a1a2e', labelcolor='white', fontsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333355')

axes[-1].set_xlabel('Distance (m)', color='white', fontsize=10)

plt.savefig('ver_nor_bahrain_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e')
print("Saved!")
plt.show()