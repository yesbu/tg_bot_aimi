import httpx
from loguru import logger
from typing import Any, Optional, Literal
from dataclasses import dataclass
from datetime import datetime   



class AirbaPaySubscriptionGateway:
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

    async def _get_token(self, payment_id: str = None) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
        }

        if payment_id:
            payload["payment_id"] = payment_id

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
    
    # page not found 
    async def create_subscription(
        self,
        amount: float | None = None,
        currency: str = "KZT",
        description: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        language: str = "ru",
        account_id: str | None = None,
        start_date: str | None = None,
        frequency: Literal["daily", "weekly", "monthly", "yearly"] = "monthly",
        success_back_url: str | None = None,
        failure_back_url: str | None = None,
        success_callback: str | None = None,
        failure_callback: str | None = None,
    ) -> dict[str, Any]:
        token = await self._get_token()

        payload: dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "email": email,
            "phone": phone,
            "language": language,
            "account_id": account_id,
            "start_date": start_date,
            "frequency": frequency,
            "success_back_url": success_back_url,
            "failure_back_url": failure_back_url,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
        }


        try:
            response = await self._client.post(
                "/api/v2/subscription",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Recurring created: account_id={account_id}, recurring_id={data.get('id')}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Create recurring failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Create recurring error: {e}")
            return {"success": False, "error": str(e)}


    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.delete(
                f"/api/v2/subscription/{subscription_id}",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            logger.info(f"Recurring cancelled: subscription_id={subscription_id}")

            return {"success": True}

        except httpx.HTTPStatusError as e:
            logger.error(f"Cancel recurring failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Cancel recurring error: {e}")
            return {"success": False, "error": str(e)}

    async def get_account_subscription(self, account_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.get(
                f"/api/v1/subscription/account/{account_id}",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Recurring status retrieved: account_id={account_id}")
            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Get recurring status failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Get recurring status error: {e}")
            return {"success": False, "error": str(e)}
        

