from src.infrastructure.persistence.models.user import User as UserModel
from src.domain.entities import User


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            telegram_id=model.telegram_id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            city=model.city,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            telegram_id=entity.telegram_id,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            city=entity.city,
            role=entity.role,
        )
    
    @staticmethod
    def update_model(model: UserModel, entity: User) -> None:
        model.username = entity.username
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.phone = entity.phone
        model.city = entity.city
        model.role = entity.role
