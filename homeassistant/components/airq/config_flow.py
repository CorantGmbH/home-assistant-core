"""Config flow for air-Q integration."""
from __future__ import annotations

import logging
from typing import Any

from aioairq import AirQ
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_ID, CONF_IP_ADDRESS, CONF_SECRET, DOMAIN

_LOGGER = logging.getLogger(__name__)

# -> adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        # vol.Required(CONF_ID): str,
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Required(CONF_SECRET): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Understand the context of this class, consider persisting the device reference
    and refactoing this solution
    """

    def __init__(self, address: str, password: str) -> None:
        """Initialize."""
        self.airq = AirQ(address, password)

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        return await self.airq.test_authentication()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # -> validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = PlaceholderHub(data[CONF_IP_ADDRESS], data[CONF_SECRET])

    if not await hub.authenticate():
        raise InvalidAuth
    config = await hub.airq.get("config")

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": f"Air-Q {config['devicename']}", "id": config["id"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for air-Q."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(info[CONF_ID])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
