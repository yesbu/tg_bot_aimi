from dishka import Provider, Scope, provide
import httpx

from src.infrastructure.payment.airbapay import AirbaPayGateway
from src.settings import Settings, settings


class PaymentProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> Settings:
        return settings
    
    @provide(scope=Scope.APP)
    async def provide_http_client(self, settings: Settings) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=settings.payment.PAYMENT_BASE_URL,
            timeout=30.0
        )
    
    @provide(scope=Scope.REQUEST)
    def provide_airba_pay_gateway(
        self, 
        settings: Settings,
        client: httpx.AsyncClient
    ) -> AirbaPayGateway:
        return AirbaPayGateway(
            user=settings.payment.PAYMENT_USER,
            password=settings.payment.PAYMENT_PASSWORD,
            terminal_id=settings.payment.PAYMENT_TERMINAL_ID,
            client=client
        )