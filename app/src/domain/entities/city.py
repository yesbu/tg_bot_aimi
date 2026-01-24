from dataclasses import dataclass


@dataclass
class City:
    id: int
    name: str
    country_id: int
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, City):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
