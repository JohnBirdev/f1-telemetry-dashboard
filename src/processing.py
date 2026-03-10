from fastf1.core import DataNotLoadedError


def prepare_lap_data(session):

    try:
        laps = session.laps
    except DataNotLoadedError:
        return None

    if laps is None or laps.empty:
        return None

    available_cols = laps.columns

    base_columns = ["Driver", "LapNumber", "LapTime", "Compound"]

    if "Stint" in available_cols:
        base_columns.append("Stint")

    laps = laps[base_columns].dropna(subset=["LapTime"]).copy()

    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    fastest_race_lap = laps["LapTimeSeconds"].min()

    laps["IsFastestOverall"] = laps["LapTimeSeconds"] == fastest_race_lap

    return laps


def get_fastest_lap_telemetry(session, driver, *, minimal: bool = True):

    driver_laps = session.laps.pick_drivers(driver)

    fastest_lap = driver_laps.pick_fastest()

    telemetry = fastest_lap.get_telemetry()

    if minimal:
        telemetry = telemetry[["Time", "X", "Y"]].copy()

    return telemetry


def _td_to_seconds(td) -> float | None:

    if td is None:
        return None

    try:
        return float(td.total_seconds())
    except Exception:
        return None


def get_fastest_lap_summary(session, driver: str) -> dict:

    driver_laps = session.laps.pick_drivers(driver)

    fastest_lap = driver_laps.pick_fastest()

    lap_time_s = _td_to_seconds(getattr(fastest_lap, "LapTime", None))
    s1_s = _td_to_seconds(getattr(fastest_lap, "Sector1Time", None))
    s2_s = _td_to_seconds(getattr(fastest_lap, "Sector2Time", None))
    s3_s = _td_to_seconds(getattr(fastest_lap, "Sector3Time", None))

    top_speed_kmh = None

    try:
        tel = fastest_lap.get_telemetry()

        if "Speed" in tel.columns:
            top_speed_kmh = float(tel["Speed"].max())

    except Exception:
        top_speed_kmh = None

    return {
        "lap_time_s": lap_time_s,
        "s1_s": s1_s,
        "s2_s": s2_s,
        "s3_s": s3_s,
        "top_speed_kmh": top_speed_kmh,
    }