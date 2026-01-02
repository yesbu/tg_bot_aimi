from dataclasses import dataclass


@dataclass
class Teacher:
    center_id: int
    name: str
    description: str | None = None
    id: int | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Teacher name cannot be empty")
    
    def update_info(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if name:
            if len(name.strip()) == 0:
                raise ValueError("Teacher name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
