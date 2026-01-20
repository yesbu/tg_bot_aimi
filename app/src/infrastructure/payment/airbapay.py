import asyncio
import httpx
from typing import Optional
from dataclasses import dataclass
from loguru import logger



class AirbaPayGateway():
    def __init__(
        self, 
        user: str, 
        password: str,
        terminal_id: str, 
        client: httpx.AsyncClient,
        payment_id: str = "",
        timeout: float = 30.0
    ):
        self._user = user
        self._password = password
        self._terminal_id = terminal_id
        self._payment_id = payment_id
        self._client = client
        self._timeout = timeout


    async def auth(self) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
            "payment_id": self._payment_id, 
        }

        try:
            response = await self._client.post(
                f"/api/v1/auth/sign-in",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            # access_token = data["access_token"]

            logger.info("Successfully authenticated with AirbaPay")
            return data

        except Exception as e:
            print(e)
            raise


    async def add_card(
        self, 
        accound_id: str, 
        phone: str, 
        email: str,
        language: str = "KZ",
        success_callback: str = "",
        failure_callback: str = "",
    ):
        
        token = await self.auth()
        token = token.get("access_token")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "account_id": accound_id,
            "phone": phone,
            "email": email,
            "language": language,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
        }

        try:
            response = await self._client.post(
                f"/api/v1/cards",
                json=payload,
                timeout=self._timeout,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            logger.info("Successfully added card to AirbaPay")
            return data
        
        except Exception as e:
            raise

    async def list_card(self, accound_id: str):
        token = await self.auth()
        token = token.get("access_token")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        url = f"/api/v1/cards/{accound_id}"

        try:
            response = await self._client.get(
                url,
                timeout=self._timeout,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            logger.info("Successfully retrieved card list from AirbaPay")
            return data

        except Exception as e:
            raise

    async def delete_card(self, card_id: str):
        token = await self.auth()
        token = token.get("access_token")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        url = f"/api/v1/cards/{card_id}"

        try:
            response = await self._client.delete(
                "",
                timeout=self._timeout,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            logger.info("Successfully deleted card from AirbaPay")
            return data

        except Exception as e:
            raise

    
    async def create_payment_v1(
        self, 
        invoice_id: str, 
        amount: float, 
        account_id: str,
        language: str = "RU",
        currency: str = "KZT",
    ):
        token = await self.auth()
        token = token.get("access_token")
        headers = {
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "invoice_id": invoice_id,
            "amount": amount,
            "account_id": account_id,
            "language": language,
            "currency": currency,
        }

        try:
            response = await self._client.post(
                f"/api/v1/payments",
                json=payload,
                timeout=self._timeout,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully created payment in AirbaPay")
            return data
        
        except Exception as e:
            raise

                



airbay_payment = AirbaPayGateway(
    client=httpx.AsyncClient(
        base_url="https://sps.airbapay.kz/acquiring-api",
    ),
    user = "Test-AMANATGENERATION",
    password = "awz4f~pz-v3!qpNd",
    terminal_id = "67b32a6bc908cc488ae9c3ed",
)



async def main():
    token = await airbay_payment.auth()
    print(f"Access token response: {token}")

    add_card = await airbay_payment.add_card(
        accound_id="77071230123",
        phone="+77071230123",
        email="example@example.com",
    )
    print(f"Add card response: {add_card}")


    list = await airbay_payment.list_card("77071230123")
    print(f"List of card {list}")


    # delete = await airbay_payment.delete_card("68e6043bb3c52fb4ab76ebf6")
    # print(f"Delete card response: {delete}")


asyncio.run(main())