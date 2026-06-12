# 🏎️ F1 Telemetry Analytics

A modular Python pipeline for race engineer-level analysis of Formula 1 telemetry data, built on the `fastf1` library with official F1 timing feeds.

Designed around a core research question: **where, precisely, does lap time delta between top competitors originate?** — quantified at the sensor level across speed, throttle, brake, and gear traces.

---

## 📁 Project Structure

f1_telemetry/

├── config.py          # Session params, driver config, color constants

├── loader.py          # Session loading, caching, quicklap selection

└── viz/

└── lap_evolution.py   # Qualifying lap time evolution plot

main.py                # Entry point

---

## 📊 Visualizations

### 1. Fastest Lap Telemetry — Max Verstappen, Bahrain GP 2025 Qualifying
Speed, throttle, brake, and gear traces across the full 5.4km lap.

![Telemetry](ver_bahrain_2025_telemetry.png)

### 2. Track Map Colored by Speed — Bahrain International Circuit
Circuit layout with speed heatmap. Purple = slow corners (~80 km/h), Yellow = full throttle straights (~310 km/h).

![Track Map](ver_bahrain_trackmap.png)

### 3. Qualifying Lap Time Evolution — Verstappen
Lap-by-lap progression across the qualifying session, with fastest lap highlighted.

![Lap Evolution](outputs/ver_lap_evolution.png)

### 4. Head-to-Head Driver Comparison — VER vs NOR
Overlaid telemetry (speed, throttle, brake, gear) with cumulative time delta panel showing exactly where each driver gains or loses time.

![Comparison](ver_nor_bahrain_comparison.png)

---

## 🔍 Key Findings

- VER and NOR are nearly identical through braking zones — the gap originates from micro-throttle application in the Sector 2 infield
- Turn 1 (~600m): hardest braking event on circuit, 300 → 80 km/h in under 100m
- Sector 2 infield (~2000–2800m): highest inter-driver differentiation zone
- VER's fastest lap: **90.42s** — set on lap 5 of qualifying

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `fastf1` | Official F1 timing & telemetry data |
| `matplotlib` | Visualization |
| `pandas` | Data manipulation |
| `numpy` | Numerical processing |

---

## 🚀 Run It Yourself

```bash
pip install fastf1 matplotlib pandas numpy
python main.py
```

Session data is cached locally in `f1_cache/` on first run. Subsequent runs are near-instant.

To change race, session, or drivers — edit `f1_telemetry/config.py`:

```python
SESSION_CONFIG = {"year": 2025, "gp": "Bahrain", "session": "Q"}
DRIVERS = {"primary": "VER", "comparison": "NOR"}
```

---

## 🔬 Roadmap

- [x] Fastest lap telemetry traces
- [x] Speed-colored track map
- [x] Qualifying lap evolution
- [x] Head-to-head telemetry overlay with time delta
- [ ] Braking zone extractor — detect and characterize braking events per corner
- [ ] Micro-sector dominance map — 50m segment analysis
- [ ] Tyre degradation model — stint lap time curve fitting
- [ ] Q1/Q2/Q3 evolution across all drivers
- [ ] Multi-race championship trend analysis

---

*Data sourced via fastf1 from official F1 timing feeds.*  
*Built by Sehaj Modi — Instrumentation & Control Engineering, NIT Jalandhar*