import fastf1
import logging
from f1_telemetry.config import SESSION_CONFIG, CACHE_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_session():
    fastf1.Cache.enable_cache(CACHE_DIR)
    cfg = SESSION_CONFIG
    logger.info(f"Loading {cfg['year']} {cfg['gp']} {cfg['session']}...")
    session = fastf1.get_session(cfg["year"], cfg["gp"], cfg["session"])
    session.load()
    logger.info("Session loaded.")
    return session


def get_driver_quicklaps(session, driver: str):
    laps = session.laps.pick_drivers(driver).pick_quicklaps().copy()
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    logger.info(f"{driver}: {len(laps)} quicklaps found.")
    return laps