# Home Assistant SaveEcoBot API Sensor (modernized for SensorEntity & UnitOf* units)
from __future__ import annotations

import asyncio
import datetime
import logging
from copy import deepcopy
from enum import Enum
from typing import List, Optional

import aiohttp
import voluptuous as vol
from pydantic import BaseModel, ValidationError

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)

# локальні модулі інтеграції
from .const import DOMAIN, CONF_CITY, CONF_STATION_IDS
from .client import StationsClient

_LOGGER = logging.getLogger(__name__)

SENSOR_DEPRECATION_HOURS = 12  # залишено для можливих перевірок

CONF_STATION_IDS_YAML = "station_ids"
CONF_CITY_NAMES_YAML = "city_names"
CONF_STATION_NAMES_YAML = "station_names"

SERVICE_SHOW_CITIES = "show_cities"
SERVICE_SHOW_CITY_STATIONS = "show_city_stations"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_STATION_IDS_YAML): cv.ensure_list,
        vol.Optional(CONF_CITY_NAMES_YAML): cv.ensure_list,
        vol.Optional(CONF_STATION_NAMES_YAML): cv.ensure_list,
    }
)


class PollutantType(Enum):
    PM2_5 = "PM2.5"
    PM10 = "PM10"
    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"
    PRESSURE = "Pressure"
    AQI = "Air Quality Index"


class Pollutant(BaseModel):
    """
    One pollutant entry from API response
    """
    pol: PollutantType
    unit: str
    time: Optional[datetime.datetime]
    value: Optional[float]
    averaging: str

    @property
    def hass_unit(self):
        """
        Map API units to Home Assistant units
        """
        _units_translation = {
            "mg/m3": CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
            # API іноді пише з помилкою "Celcius" — підстрахуємось
            "Celcius": UnitOfTemperature.CELSIUS,
            "Celsius": UnitOfTemperature.CELSIUS,
            "%": PERCENTAGE,
            "hPa": UnitOfPressure.HPA,
        }
        return _units_translation.get(self.unit, self.unit)


class SaveEcoBotSensorModel(BaseModel):
    """
    Represents data model for HA sensor
    """
    name: str
    unique_id: str
    station_id: str
    sensor_type: PollutantType
    state: Optional[float]
    device_state_attributes: dict
    deprecated: bool = True


class Station(BaseModel):
    """
    SaveEcoBot station model
    """
    id: str
    cityName: str
    stationName: str
    localName: str
    timezone: str
    latitude: float
    longitude: float
    pollutants: List[Pollutant]

    @property
    def slug(self) -> str:
        return f"{self.id}_{self.cityName}".lower()

    def sensors(self) -> List[SaveEcoBotSensorModel]:
        """
        Convert pollutants into HA-friendly sensor models
        """
        station_sensors: List[SaveEcoBotSensorModel] = []
        common_attrs = {
            "city": self.cityName,
            "address": self.stationName,
            "local_name": self.localName,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
        for p in self.pollutants:
            _updated_at = (
                datetime.datetime.strftime(p.time, "%d.%m.%Y, %H:%M:%S")
                if p.time
                else None
            )
            attrs = {
                "updated_at": _updated_at,
                "unit_of_measurement": p.hass_unit,
                "averaging": p.averaging,
                **common_attrs,
            }
            station_sensor = SaveEcoBotSensorModel(
                name=f"{p.pol.name} ({self.cityName}, {self.stationName})",
                unique_id=f"{self.slug}_{p.pol.name.lower()}",
                station_id=self.id,
                sensor_type=p.pol,
                state=p.value,
                device_state_attributes=attrs,
                deprecated=False,
            )
            station_sensors.append(station_sensor)
        return station_sensors


class SaveEcoBotSensor(SensorEntity):
    """SaveEcoBot Sensor."""

    def __init__(self, client: StationsClient, sensor_model: SaveEcoBotSensorModel):
        self._client = client
        self._model = sensor_model
        self._name = sensor_model.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._model.unique_id

    @property
    def native_value(self):
        if self._model.deprecated:
            return None
        return self._model.state if self._model else None

    @property
    def native_unit_of_measurement(self):
        return self._model.device_state_attributes.get("unit_of_measurement")

    @property
    def extra_state_attributes(self):
        # не дублюємо UoM у атрибути
        attrs = dict(self._model.device_state_attributes)
        attrs.pop("unit_of_measurement", None)
        return attrs

    @property
    def device_class(self):
        t = self._model.sensor_type
        if t == PollutantType.TEMPERATURE:
            return SensorDeviceClass.TEMPERATURE
        if t == PollutantType.PRESSURE:
            return SensorDeviceClass.PRESSURE
        if t == PollutantType.HUMIDITY:
            return SensorDeviceClass.HUMIDITY
        if t == PollutantType.PM2_5:
            return SensorDeviceClass.PM25
        if t == PollutantType.PM10:
            return SensorDeviceClass.PM10
        if t == PollutantType.AQI:
            return SensorDeviceClass.AQI
        return None

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    async def async_update(self):
        await self._client.update()
        self._model = self._client.get_sensor(
            station_id=self._model.station_id, sensor_type=self._model.sensor_type
        )
        if self._model is None:
            _LOGGER.error(
                "Error updating data from sensor %s! Got no data from API.", self._name
            )
            return
        _LOGGER.debug("Updated: %s", self.name)


# ===== YAML шлях (залишається для зворотної сумісності) =====
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up SaveEcoBot sensor platform via YAML."""
    client = StationsClient()

    try:
        await client.update(force=True)
    except (
        aiohttp.client_exceptions.ClientConnectorError,
        asyncio.TimeoutError,
    ) as err:
        _LOGGER.exception("Failed to connect to SaveEcoBot servers")
        raise PlatformNotReady from err

    station_ids = config.get(CONF_STATION_IDS_YAML)
    city_names = config.get(CONF_CITY_NAMES_YAML)
    station_names = config.get(CONF_STATION_NAMES_YAML)

    stations_iter = client.filter_stations(
        station_ids=station_ids, city_names=city_names, station_names=station_names
    )

    sensors: list[SaveEcoBotSensor] = []
    for station in stations_iter:
        sensors.extend(
            [SaveEcoBotSensor(client=client, sensor_model=s) for s in station.sensors()]
        )

    async_add_entities(sensors)
    _LOGGER.debug("Setup (YAML) done. %d sensors added.", len(sensors))

    # додаткові сервіси як у початковій версії
    async def show_cities_handler(_):
        cities = "\n".join(client.cities())
        _LOGGER.debug("`show_cities` service called. Cities: %s", cities)
        hass.components.persistent_notification.async_create(
            f"Available cities:\n{cities}",
            title="SaveEcoBot Cities",
            notification_id="save_eco_bot_show_cities",
        )

    async def show_city_stations_handler(service):
        _LOGGER.debug("`show_city_stations` called. Data: %s", service.data)
        city = service.data.get("city", "<please provide `city: city_name` in service data>")
        data = client.city_stations(city)
        message = "\n".join([f"{s_id} - {s_addr}" for s_id, s_addr in data]) if data else ""
        hass.components.persistent_notification.async_create(
            f"Stations in {city}:\n\n{message}",
            title="SaveEcoBot Stations",
            notification_id="save_eco_bot_show_city_stations",
        )

    hass.services.async_register(DOMAIN, SERVICE_SHOW_CITIES, show_cities_handler)
    hass.services.async_register(DOMAIN, SERVICE_SHOW_CITY_STATIONS, show_city_stations_handler)


# ===== Нове: async_setup_entry для UI-настройки (Config Flow) =====
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensors from Config Entry (UI)."""
    # Створюємо власний клієнт (не залежимо від hass.data, щоб уникнути циклів)
    client = StationsClient()

    # options з config_flow: city + station_ids
    city = entry.options.get(CONF_CITY)
    station_ids = entry.options.get(CONF_STATION_IDS, [])

    try:
        await client.update(force=True)
    except (
        aiohttp.client_exceptions.ClientConnectorError,
        asyncio.TimeoutError,
    ) as err:
        _LOGGER.exception("Failed to connect to SaveEcoBot servers")
        raise PlatformNotReady from err

    # якщо задані station_ids — беремо їх; інакше, якщо є city — беремо всі станції цього міста
    if station_ids:
        stations_iter = client.filter_stations(station_ids=station_ids)
    elif city:
        stations_iter = client.filter_stations(city_names=[city])
    else:
        stations_iter = client.filter_stations()

    sensors: list[SaveEcoBotSensor] = []
    for station in stations_iter:
        sensors.extend([SaveEcoBotSensor(client=client, sensor_model=s) for s in station.sensors()])

    async_add_entities(sensors)
    _LOGGER.debug("Entry setup done. %d sensors added.", len(sensors))
