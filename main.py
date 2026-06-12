from f1_telemetry.loader import load_session, get_driver_quicklaps
from f1_telemetry.viz.lap_evolution import plot_lap_evolution
from f1_telemetry.analysis.delta import plot_telemetry_comparison
from f1_telemetry.analysis.braking import extract_braking_zones, plot_braking_zones
from f1_telemetry.config import DRIVERS

if __name__ == "__main__":
    session = load_session()

    laps_a = get_driver_quicklaps(session, DRIVERS["primary"])
    laps_b = get_driver_quicklaps(session, DRIVERS["comparison"])

    fastest_a = laps_a.pick_fastest()
    fastest_b = laps_b.pick_fastest()

    # Lap evolution
    plot_lap_evolution(laps_a, DRIVERS["primary"])

    # Head-to-head delta
    plot_telemetry_comparison(fastest_a, fastest_b, DRIVERS["primary"], DRIVERS["comparison"])

    # Braking zone analysis
    tel_a = fastest_a.get_telemetry().add_distance()
    zones = extract_braking_zones(tel_a)
    print("\n--- Braking Zones ---")
    print(zones.to_string(index=False))
    plot_braking_zones(tel_a, zones, DRIVERS["primary"])