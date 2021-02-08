"""Sensor platform for the Flipr's pool_sensor."""
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, CONF_FLIPR_ID

from . import FliprEntity

SENSORS = {
    "chlorine": {
        "unit": "mV",
        "icon": "mdi:pool",
        "name": "Chlorine",
        "device_class": None,
    },
    "ph": {"unit": "ph", "icon": "mdi:pool", "name": "PH", "device_class": None},
    "temperature": {
        "unit": TEMP_CELSIUS,
        "icon": "mdi:coolant-temperature",
        "name": "Water Temp",
        "device_class": DEVICE_CLASS_TEMPERATURE,
    },
    "date_time": {
        "unit": None,
        "icon": "mdi:clock",
        "name": "Date Measure",
        "device_class": DEVICE_CLASS_TIMESTAMP,
    },
    "red_ox": {
        "unit": "mV",
        "icon": "mdi:pool",
        "name": "Red OX",
        "device_class": None,
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors_list = []
    for sensor in SENSORS:
        sensors_list.append(
            FliprSensor(coordinator, config_entry.data[CONF_FLIPR_ID], sensor)
        )

    async_add_entities(sensors_list, True)


class FliprSensor(FliprEntity, Entity):
    """Sensor representing FliprSensor data."""

    @property
    def name(self):
        """Return the name of the particular component."""
        return f"Flipr {self.flipr_id} {SENSORS[self.info_type]['name']}"

    @property
    def state(self):
        """State of the sensor."""
        return self.coordinator.data[self.info_type]

    @property
    def device_class(self):
        """Return the device class."""
        return SENSORS[self.info_type]["device_class"]

    @property
    def icon(self):
        """Return the icon."""
        return SENSORS[self.info_type]["icon"]

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return SENSORS[self.info_type]["unit"]

    @property
    def device_state_attributes(self):
        """Return device attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}
