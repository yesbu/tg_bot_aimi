from src.infrastructure.persistence.models.center import Center as CenterModel
from src.domain.entities import Center


class CenterMapper:
    @staticmethod
    def to_entity(model: CenterModel) -> Center:
        return Center(
            id=model.id,
            partner_id=model.partner_id,
            name=model.name,
            city=model.city,
            address=model.address,
            phone=model.phone,
            category=model.category,
            description=model.description,
            logo=model.logo,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Center) -> CenterModel:
        return CenterModel(
            id=entity.id,
            partner_id=entity.partner_id,
            name=entity.name,
            city=entity.city,
            address=entity.address,
            phone=entity.phone,
            category=entity.category,
            description=entity.description,
            logo=entity.logo,
            status=entity.status,
        )
    
    @staticmethod
    def update_model(model: CenterModel, entity: Center) -> None:
        model.name = entity.name
        model.city = entity.city
        model.address = entity.address
        model.phone = entity.phone
        model.category = entity.category
        model.description = entity.description
        model.logo = entity.logo
        model.status = entity.status
