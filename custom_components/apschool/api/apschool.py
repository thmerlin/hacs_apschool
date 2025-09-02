"""Sample API Client."""

# from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any
from urllib.parse import urljoin

import aiohttp
import async_timeout

from custom_components.apschool.api.helpers import UnreadMessage, UserData

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ApschoolApiClientError(Exception):
    """Exception to indicate a general API error."""


class ApschoolApiClientCommunicationError(ApschoolApiClientError):
    """Exception to indicate a communication error."""


class ApschoolApiClientAuthenticationError(ApschoolApiClientError):
    """Exception to indicate an authentication error."""


class ApschoolApiClient:
    """APSchool API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """API Client."""
        self._username = username
        self._password = password
        self._base_url = base_url
        self._session = session
        self.token = None
        self.current_user_id = None

    def _set_headers(self) -> dict:
        """Set the request headers with authenrization

        Returns:
            dict: the key-value pairs for the different headers
        """

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _async_authenticate(self) -> list[Any]:
        """Authenticate against the API and store the bearer token and the user_id"""
        url = urljoin(self._base_url, "authentification")
        data = {
            "identite": self._username,
            "motDePasse": self._password,
        }

        json_response = await self._api_wrapper(
            method="POST", url=url, data=data, headers=self._set_headers()
        )

        self.token = json_response.get("token")
        # self.user_id = json_response.get("liaisons")[0].get("utilisateurId")
        return json_response.get("liaisons")

    async def _async_change_link(self, from_id: int, to_id: int):
        """Change link is a method that set a new token for the "to_id",
            meaning that any request with that token will be dedicated to that ID"""
        url = urljoin(self._base_url,
                      f"authentification/{from_id}/liaisons/{to_id}")
        json_response = await self._api_wrapper(
            method="POST", url=url, data=None, headers=self._set_headers()
        )

        self.token = json_response.get("token")

    async def _async_get_balance(self):
        """Get balance of user

        Returns:
            list[UnreadMessage]: List of unread messages (only the date and a title)
            None: When there is no unread message
        """
        url = urljoin(
            self._base_url, f"/mediatr-utilisateurs/{
                self.current_user_id}/comptes"
        )

        json_response = await self._api_wrapper(
            method="GET", url=url, data=None, headers=self._set_headers()
        )

        balance = [
            res.get("solde") for res in json_response["items"] if res["typeCompte"] == 0
        ]

        return balance[0] if len(balance) > 0 else 0

    async def _async_get_unread_messages(self):
        """Get unread messages

        Returns:
            list[UnreadMessage]: List of unread messages (only the date and a title)
            None: When there is no unread message
        """
        url = urljoin(self._base_url,
                      f"/utilisateurs/{self.current_user_id}/messages")

        json_response = await self._api_wrapper(
            method="GET", url=url, data=None, headers=self._set_headers()
        )

        messages = [
            UnreadMessage(res)
            for res in json_response["items"]
            if res["ouvert"] is False
        ]

        return messages if len(messages) > 0 else None

    async def _async_get_due_amount(self):
        """Get due amount from fees and others

        Returns:
            Total amount still due
        """
        url = urljoin(self._base_url,
                      "/mediatr-utilisateurs/evenements-impayes")
        # params = {"paye": "false", "refuse": "false"}

        json_response = await self._api_wrapper(
            method="GET", url=url, data=None, headers=self._set_headers(),
        )

        total_amount = sum([float(res["totalAPayer"])
                            for res in json_response["items"]])

        return total_amount

    async def async_get_user_data(self) -> list[UserData]:
        """Get all the user data from the APSchool website

        Returns:
            List of UserData: The full data
        """
        links = await self._async_authenticate()

        users = []
        for link in links:
            self.current_user_id = link.get("utilisateurId")
            target_identifier = link.get("identifiantCible")
            await self._async_change_link(
                from_id=self.current_user_id, to_id=target_identifier
            )

            json_response = await self._api_wrapper(
                method="GET",
                url=urljoin(self._base_url, "/session"),
                data=None,
                headers=self._set_headers(),
            )

            user_data = UserData(
                user_id=self.current_user_id,
                firstname=json_response.get("prenom"),
                lastname=json_response.get("nom"),
                school_class=json_response.get("classe").get("libelle"),
                balance=await self._async_get_balance(),
                unread_messages=await self._async_get_unread_messages(),
                due_amount=await self._async_get_due_amount(),
            )

            _LOGGER.debug("Data retrieved: %s", user_data.to_json())
            users.append(user_data)

        return users

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )
                if response.status in (400, 401, 403):
                    raise ApschoolApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApschoolApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApschoolApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except ApschoolApiClientAuthenticationError as exception:
            raise exception
        except Exception as exception:  # pylint: disable=broad-except
            raise ApschoolApiClientError(
                "Something really wrong happened!"
            ) from exception
