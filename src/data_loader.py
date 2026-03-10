import os

import fastf1

_CACHE_ENABLED = False

def setup_cache():
    global _CACHE_ENABLED
    if _CACHE_ENABLED:
        return

    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)
    _CACHE_ENABLED = True


def get_schedules(year: int):
    setup_cache()
    schedules = fastf1.get_event_schedule(year)
    
    races = schedules[schedules['EventName'].str.contains("Test") == False]
    return races

def load_session(
    year: int,
    round_number: int,
    session_type: str = "R",
    *,
    telemetry: bool = False,
    laps: bool = True,
    weather: bool = False,
):
    setup_cache()
    session = fastf1.get_session(year, round_number, session_type)
    session.load(telemetry=telemetry, laps=laps, weather=weather)
    return session