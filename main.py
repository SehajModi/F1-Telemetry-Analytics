from f1_telemetry.loader import load_session, get_driver_quicklaps
from f1_telemetry.viz.lap_evolution import plot_lap_evolution
from f1_telemetry.config import DRIVERS

if __name__ == "__main__":
    session = load_session()
    laps = get_driver_quicklaps(session, DRIVERS["primary"])
    plot_lap_evolution(laps, DRIVERS["primary"])