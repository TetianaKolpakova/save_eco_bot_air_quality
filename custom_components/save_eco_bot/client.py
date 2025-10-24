# client.py
from __future__ import annotations

import asyncio
import datetime
import logging
from copy import deepcopy
from typing import List, Optional

import aiohttp
from pydantic import BaseModel, ValidationError  # pydantic v2 сумісно

_LOGGER = logging.getLogger(__name__)

class StationsClient:
    """Thin API client for SaveEcoBot."""
    _api_url = "https://api.saveecobot.com/output.json"

    def __init__(self):
        self.stations: List[BaseModel] = []
        self.updated_at = datetime.datetime.now()

    async def update(self, force: bool = False) -> bool:
        if (datetime.datetime.now() - self.updated_at < datetime.timedelta(seconds=30)) and not force:
            _LOGGER.debug("Update called, using cached values")
            return True

        _LOGGER.info("Performing SaveEcoBot API call...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self._api_url, timeout=20) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed API response %s: %s", resp.status, resp.content)
                    return False
                stations_resp = await resp.json()

        from .sensor import Station  # імпорт тут, щоб уникнути циклів
        self.stations = []
        for station in stations_resp:
            try:
                self.stations.append(Station(**station))
            except ValidationError as e:
                _LOGGER.error("Validation error %s, skipping: %s", e, station)
                continue

        self.updated_at = datetime.datetime.now()
        _LOGGER.debug("Updated from API call. %d stations", len(self.stations))
        return True

    def filter_stations(
        self,
        station_ids: list[str] | None = None,
        city_names: list[str] | None = None,
        station_names: list[str] | None = None,
    ):
        station_ids = station_ids or []
        city_names = city_names or []
        station_names = station_names or []

        _filters = {
            "station_id": lambda s: s.id in station_ids,
            "city_name": lambda s: s.cityName in city_names,
            "station_name": lambda s: s.stationName in station_names,
        }

        fs = deepcopy(self.stations)
        if station_ids:
            fs = filter(_filters["station_id"], fs)
        if city_names:
            fs = filter(_filters["city_name"], fs)
        if station_names:
            fs = filter(_filters["station_name"], fs)
        return fs

    def cities(self) -> list[str]:
        return sorted(set(c.cityName for c in self.stations))

    def city_stations(self, city: str) -> list[tuple[str, str]]:
        if city not in self.cities():
            return []
        city_stations = self.filter_stations(city_names=[city])
        return [(c.id, c.stationName) for c in city_stations]

    def get_sensor(self, station_id: str, sensor_type) -> Optional[BaseModel]:
        try:
            stations = list(self.filter_stations(station_ids=[station_id]))
            if not stations:
                return None
            station = stations[0]
            sensor = [p for p in station.sensors() if p.sensor_type is sensor_type]
            return sensor[0] if sensor else None
        except Exception as exc:
            _LOGGER.error("get_sensor error: %s", exc)
            return None
