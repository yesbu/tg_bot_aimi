from dataclasses import dataclass


@dataclass
class Category:
    id: int
    name: str
    is_active: bool = True
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Category):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def activate(self) -> None:
        self.is_active = True
    
    def deactivate(self) -> None:
        self.is_active = False
