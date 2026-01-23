import httpx
from loguru import logger
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime   



class AirbaPayWebhookGateway:
    def __init__(
        self,
        client: httpx.AsyncClient,
        user: str,
        password: str,
        terminal_id: str,
        timeout: float = 30.0,
    ):
        self._client = client
        self._user = user
        self._password = password
        self._terminal_id = terminal_id
        self._timeout = timeout

    async def _get_token(self, payment_id: str = None, payout_id: str = None) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
        }

        if payment_id:
            payload["payment_id"] = payment_id

        if payout_id:
            payload["payout_id"] = payout_id

        try:
            response = await self._client.post(
                "/api/v1/auth/sign-in",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            token = data.get("access_token")

            if not token:
                raise ValueError("No access_token in response")

            logger.debug("Successfully authenticated with AirbaPay")
            return token

        except httpx.HTTPStatusError as e:
            logger.error(f"AirbaPay auth failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"AirbaPay auth error: {e}")
            raise

    def _get_auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
    

