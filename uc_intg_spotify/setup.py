"""Spotify setup flow. :copyright: (c) 2024 by Meir Miyara. :license: MPL-2.0"""
from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any

from ucapi import RequestUserInput
from ucapi_framework import BaseSetupFlow

from uc_intg_spotify.client import SpotifyClient
from uc_intg_spotify.config import SpotifyDeviceConfig

_LOG = logging.getLogger(__name__)

_IDENTIFIER_RE = re.compile(r"[^a-z0-9_]+")


class SpotifySetupFlow(BaseSetupFlow[SpotifyDeviceConfig]):
    """Setup flow for Spotify integration using OAuth2."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client_id: str = ""
        self._client_secret: str = ""

    def get_manual_entry_form(self) -> RequestUserInput:
        return RequestUserInput(
            {"en": "Spotify Setup"},
            [
                {
                    "id": "info",
                    "label": {"en": "Setup Instructions"},
                    "field": {
                        "label": {
                            "value": {
                                "en": "IMPORTANT: Spotify Premium is required.\n\n"
                                "1. Go to https://developer.spotify.com/dashboard\n"
                                "2. Log in and click 'Create App'\n"
                                "3. App Name: 'UC Remote Integration'\n"
                                "4. Redirect URI: https://example.com/callback\n"
                                "5. Check 'Web API' and save\n"
                                "6. Copy Client ID and Client Secret below\n\n"
                                "\n\n"
                                "Note: You can add multiple Spotify accounts by running setup again.\n\n"
                            }
                        }
                    },
                },
                {
                    "id": "client_id",
                    "label": {"en": "Spotify Client ID"},
                    "field": {"text": {"value": ""}},
                },
                {
                    "id": "client_secret",
                    "label": {"en": "Spotify Client Secret"},
                    "field": {"text": {"value": ""}},
                },
            ],
        )

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> SpotifyDeviceConfig | RequestUserInput:
        if "auth_code" in input_values:
            return await self._handle_auth_code(input_values)

        client_id = input_values.get("client_id", "").strip()
        client_secret = input_values.get("client_secret", "").strip()

        if not client_id or not client_secret:
            raise ValueError("Both Client ID and Client Secret are required")

        self._client_id = client_id
        self._client_secret = client_secret

        return self._auth_form()

    async def _handle_auth_code(
        self, input_values: dict[str, Any]
    ) -> SpotifyDeviceConfig | RequestUserInput:
        auth_input = input_values.get("auth_code", "").strip()
        if not auth_input:
            return self._auth_form("Paste the Spotify callback URL or authorization code.")

        auth_code, error = _extract_auth_code(auth_input)
        if error:
            return self._auth_form(error)

        client = SpotifyClient()
        try:
            token_data = await client.exchange_code_for_token(
                auth_code, self._client_id, self._client_secret
            )

            if not token_data:
                return self._auth_form(
                    "Spotify rejected that callback/code. Start the Spotify authorization again and paste the new callback URL."
                )

            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
            expires_in = token_data.get("expires_in", 3600)

            client.set_tokens(access_token, refresh_token)
            user = await client.get_current_user()
        finally:
            await client.close()

        account_id = _account_id(user)
        account_name = _account_name(user, account_id)

        import time

        return SpotifyDeviceConfig(
            identifier=f"spotify_{_safe_identifier(account_id)}",
            name=f"Spotify ({account_name})",
            client_id=self._client_id,
            client_secret=self._client_secret,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=int(time.time()) + expires_in - 60,
        )

    def _auth_form(self, error: str = "") -> RequestUserInput:
        client = SpotifyClient()
        auth_url = client.get_authorization_url(self._client_id)
        instructions = (
            "1. Click the URL below to open in a browser\n"
            "2. Log in and authorize the application\n"
            "3. You'll see 'page not found' - this is normal!\n"
            "4. Copy the URL from your browser's address bar\n"
            "5. Paste the URL below"
        )
        if error:
            instructions = f"{error}\n\n{instructions}"

        return RequestUserInput(
            {"en": "Spotify Authentication"},
            [
                {
                    "id": "instructions",
                    "label": {"en": "Authentication Instructions"},
                    "field": {"label": {"value": {"en": instructions}}},
                },
                {
                    "id": "spotify_url",
                    "label": {"en": "Spotify Authorization URL"},
                    "field": {"text": {"value": auth_url, "read_only": True}},
                },
                {
                    "id": "auth_code",
                    "label": {"en": "Paste Code or Full URL"},
                    "field": {"text": {"value": "", "placeholder": "Paste here..."}},
                },
            ],
        )


def _account_id(user: dict[str, Any] | None) -> str:
    if not user:
        return "account"
    return str(user.get("id") or user.get("email") or user.get("display_name") or "account")


def _account_name(user: dict[str, Any] | None, fallback: str) -> str:
    if not user:
        return fallback
    return str(user.get("display_name") or user.get("email") or user.get("id") or fallback)


def _safe_identifier(value: str) -> str:
    safe = _IDENTIFIER_RE.sub("_", value.lower()).strip("_")
    return safe or "account"


def _extract_auth_code(auth_input: str) -> tuple[str, str]:
    if "://" not in auth_input and "code=" not in auth_input:
        return auth_input, ""

    if "://" in auth_input:
        parsed = urllib.parse.urlparse(auth_input)
        params = urllib.parse.parse_qs(parsed.query or parsed.fragment)
    else:
        params = urllib.parse.parse_qs(auth_input.lstrip("?"))

    spotify_error = params.get("error", [""])[0]
    if spotify_error:
        return "", f"Spotify returned an authorization error: {spotify_error}."

    code = params.get("code", [""])[0].strip()
    if not code:
        return "", "That callback URL does not contain a Spotify authorization code."

    return code, ""
