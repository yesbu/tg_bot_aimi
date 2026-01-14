from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Language(Base):
    __tablename__ = "languages"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    code: Mapped[str] = mapped_column(
        String(10), 
        unique=True, 
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )

    def __repr__(self):
        return f"<Language(code={self.code}, name={self.name})>"