import httpx
from loguru import logger
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime   



class AirbaPayCardGateway():
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

    async def _get_token(self) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
        }

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

    async def add_card(
        self,
        account_id: str,
        phone: str | None = None,
        email: str | None = None,
        success_back_url: str | None = None,
        failure_back_url: str | None = None,
        success_callback: str | None = None,
        failure_callback: str | None = None,
        language: str = "ru",

    ) -> dict[str, Any]:
        
        token = await self._get_token()

        payload = {
            "account_id": account_id,
            "phone": phone,
            "email": email,
            "language": language,
            "success_back_url": success_back_url,
            "failure_back_url": failure_back_url,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
        }

        try:
            response = await self._client.post(
                "/api/v1/cards",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Card added for account_id={account_id}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Add card failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Add card error: {e}")
            return {"success": False, "error": str(e)}
        
        
    async def list_card(self, account_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.get(
                f"/api/v1/cards/{account_id}",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Cards retrieved for account_id={account_id}")

            return {"success": True, "cards": data}

        except httpx.HTTPStatusError as e:
            logger.error(f"List cards failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"List cards error: {e}")
            return {"success": False, "error": str(e)}

    async def delete_card(self, card_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.delete(
                f"/api/v1/cards/{card_id}",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            logger.info(f"Card deleted: card_id={card_id}")

            return {"success": True}

        except httpx.HTTPStatusError as e:
            logger.error(f"Delete card failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Delete card error: {e}")
            return {"success": False, "error": str(e)}
    