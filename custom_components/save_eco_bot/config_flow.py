from __future__ import annotations

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_CITY, CONF_STATION_IDS
from .client import StationsClient

_LOGGER = logging.getLogger(__name__)


def _city_dropdown_schema(cities: list[str], default_city: str | None = None) -> vol.Schema:
    """Dropdown міст (без поля пошуку)."""
    return vol.Schema(
        {
            vol.Required(CONF_CITY, default=default_city or (cities[0] if cities else "")): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=cities,
                    multiple=False,
                    mode="dropdown",  # стандартний скрол
                )
            ),
        }
    )


def _stations_schema(station_ids: list[str]) -> vol.Schema:
    """Dropdown станцій: за замовчуванням пусто, select_all = False."""
    return vol.Schema(
        {
            vol.Required("select_all", default=False): selector.BooleanSelector(),
            vol.Optional(CONF_STATION_IDS, default=[]): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=station_ids,
                    multiple=True,
                    mode="dropdown",
                )
            ),
        }
    )


class SaveEcoBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для SaveEcoBot."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Крок 1: вибір міста."""
        if user_input:
            if user_input.get(CONF_CITY):
                self._city = user_input[CONF_CITY]
                return await self.async_step_stations()

        client = StationsClient()
        await client.update(force=True)
        cities = client.cities()

        if not cities:
            return self.async_abort(reason="no_cities")

        return self.async_show_form(
            step_id="user",
            data_schema=_city_dropdown_schema(cities),
            description_placeholders={"map_link": "https://www.saveecobot.com/maps"},
        )

    async def async_step_stations(self, user_input=None):
        """Крок 2: вибір станцій."""
        client = StationsClient()
        await client.update(force=True)
        stations = client.city_stations(self._city)
        all_ids = [sid for sid, _ in stations]

        if not all_ids:
            return self.async_create_entry(
                title=f"SaveEcoBot: {self._city}",
                data={},
                options={CONF_CITY: self._city, CONF_STATION_IDS: []},
            )

        if user_input is not None:
            select_all = user_input.get("select_all", False)
            picked_ids = user_input.get(CONF_STATION_IDS, [])
            options_payload = {
                CONF_CITY: self._city,
                CONF_STATION_IDS: [] if select_all else picked_ids,
            }
            return self.async_create_entry(
                title=f"SaveEcoBot: {self._city}",
                data={},
                options=options_payload,
            )

        return self.async_show_form(
            step_id="stations",
            data_schema=_stations_schema(all_ids),
            description_placeholders={"map_link": "https://www.saveecobot.com/maps"},
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SaveEcoBotOptionsFlowHandler(config_entry)


class SaveEcoBotOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow — перевибір міста/станцій (без автоселекту)."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._entry = config_entry
        self._city = config_entry.options.get(CONF_CITY)

    async def async_step_init(self, user_input=None):
        return await self.async_step_city()

    async def async_step_city(self, user_input=None):
        client = StationsClient()
        await client.update(force=True)
        cities = client.cities()

        if not cities:
            return self.async_abort(reason="no_cities")

        if user_input and user_input.get(CONF_CITY):
            self._city = user_input[CONF_CITY]
            return await self.async_step_stations()

        return self.async_show_form(
            step_id="city",
            data_schema=_city_dropdown_schema(cities, default_city=self._city),
            description_placeholders={"map_link": "https://www.saveecobot.com/maps"},
        )

    async def async_step_stations(self, user_input=None):
        client = StationsClient()
        await client.update(force=True)
        stations = client.city_stations(self._city)
        all_ids = [sid for sid, _ in stations]

        if user_input is not None:
            select_all = user_input.get("select_all", False)
            picked_ids = user_input.get(CONF_STATION_IDS, [])
            return self.async_create_entry(
                title="",
                data={
                    CONF_CITY: self._city,
                    CONF_STATION_IDS: [] if select_all else picked_ids,
                },
            )

        return self.async_show_form(
            step_id="stations",
            data_schema=_stations_schema(all_ids),
            description_placeholders={"map_link": "https://www.saveecobot.com/maps"},
        )
