from enum import StrEnum, IntEnum


class PaymentStatus(StrEnum):
    NEW = "new"
    SECURE_3D = "secure3D"
    AUTH = "auth"
    SUCCESS = "success"
    ERROR = "error"
    RETURN = "return"
    REFUND = "refund"
    UNBLOCK = "unblock"


    @property
    def description(self) -> str:
        descriptions = {
            self.NEW: "Платеж создан и ссылка на платежную форму сформирована. Клиент не ввел данные карты",
            self.SECURE_3D: "Платеж на проверке 3DS",
            self.AUTH: "Платеж авторизован. Средства заблокированы. Необходимо подтвердить платеж",
            self.SUCCESS: "Платеж обработан успешно",
            self.ERROR: "Платеж в состоянии ошибка",
            self.RETURN: "Платеж возвращен полностью",
            self.REFUND: "Платеж возвращен частично",
            self.UNBLOCK: "Платеж разблокирован",
        }
        return descriptions.get(self, "Неизвестный статус платежа")
    
