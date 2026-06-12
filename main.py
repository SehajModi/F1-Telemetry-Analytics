from f1_telemetry.loader import load_session, get_driver_quicklaps
from f1_telemetry.viz.lap_evolution import plot_lap_evolution
from f1_telemetry.analysis.delta import plot_telemetry_comparison
from f1_telemetry.config import DRIVERS

if __name__ == "__main__":
    session = load_session()

    laps_a = get_driver_quicklaps(session, DRIVERS["primary"])
    laps_b = get_driver_quicklaps(session, DRIVERS["comparison"])

    plot_lap_evolution(laps_a, DRIVERS["primary"])

    fastest_a = laps_a.pick_fastest()
    fastest_b = laps_b.pick_fastest()
    plot_telemetry_comparison(fastest_a, fastest_b, DRIVERS["primary"], DRIVERS["comparison"])