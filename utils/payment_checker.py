"""
Автоматическая проверка статуса платежей
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PaymentChecker:
    """Автоматическая проверка статуса pending платежей"""
    
    def __init__(self, db, payment_service, check_interval: int = 60):
        self.db = db
        self.payment_service = payment_service
        self.check_interval = check_interval  # Интервал проверки в секундах
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    async def check_pending_payments(self):
        """Проверка всех pending платежей"""
        try:
            # Получаем все pending платежи старше 1 минуты
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db_conn:
                db_conn.row_factory = aiosqlite.Row
                async with db_conn.execute("""
                    SELECT payment_id, user_id, subscription_id, airba_payment_id, created_at
                    FROM payments
                    WHERE status = 'pending'
                    AND datetime(created_at) < datetime('now', '-1 minute')
                    ORDER BY created_at DESC
                    LIMIT 10
                """) as cursor:
                    payments = await cursor.fetchall()
            
            for payment_row in payments:
                payment = dict(payment_row)
                payment_id = payment['payment_id']
                user_id = payment['user_id']
                
                try:
                    result = await self.payment_service.get_payment_status(payment_id, user_id)
                    
                    if result.get("success"):
                        status = result.get("status", "pending")
                        
                        if status == "success":
                            # Платеж успешен - активируем абонемент
                            subscription_id = payment.get("subscription_id")
                            if subscription_id:
                                await self._activate_subscription(user_id, subscription_id)
                                logger.info(f"Платеж {payment_id} успешен, абонемент {subscription_id} активирован")
                    
                except Exception as e:
                    logger.error(f"Ошибка при проверке платежа {payment_id}: {e}")
        
        except Exception as e:
            logger.error(f"Ошибка при проверке pending платежей: {e}", exc_info=True)
    
    async def _activate_subscription(self, user_id: int, subscription_id: int):
        """Активация абонемента после успешной оплаты"""
        try:
            from utils.qr_generator import generate_subscription_qr
            import aiosqlite
            
            # Генерируем QR-код
            qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
            
            # Обновляем QR-код в базе данных
            async with aiosqlite.connect(self.db.db_path) as db_conn:
                await db_conn.execute(
                    "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                    (qr_id, subscription_id)
                )
                await db_conn.commit()
            
            logger.info(f"Абонемент {subscription_id} активирован с QR-кодом {qr_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при активации абонемента {subscription_id}: {e}", exc_info=True)
    
    async def start(self):
        """Запуск автоматической проверки"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Автоматическая проверка платежей запущена")
    
    async def stop(self):
        """Остановка автоматической проверки"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Автоматическая проверка платежей остановлена")
    
    async def _run(self):
        """Основной цикл проверки"""
        while self.running:
            try:
                await self.check_pending_payments()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле проверки платежей: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

