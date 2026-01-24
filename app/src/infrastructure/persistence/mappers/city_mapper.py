from src.domain.entities.city import City as CityEntity
from src.infrastructure.persistence.models.city import City as CityModel


class CityMapper:
    @staticmethod
    def to_entity(model: CityModel, name: str) -> CityEntity:
        return CityEntity(
            id=model.id,
            name=name,
            country_id=model.country_id
        )
    
    @staticmethod
    def to_model(entity: CityEntity) -> CityModel:
        return CityModel(
            id=entity.id,
            country_id=entity.country_id
        )
