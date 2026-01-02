from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .country import Country
    from .language import Language


class City(Base):
    __tablename__ = "cities"
    
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    country: Mapped["Country"] = relationship(back_populates="cities")

    translations: Mapped[list["CityTranslation"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan"
    )


class CityTranslation(Base):
    __tablename__ = "city_translations"
    
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"), 
        nullable=False
    )
    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id", ondelete="CASCADE"), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        index=True
    )
    
    city: Mapped["City"] = relationship(back_populates="translations")
    
    language: Mapped["Language"] = relationship()
    
    __table_args__ = (
        UniqueConstraint('city_id', 'language_id', name='uq_city_language'),
        Index('idx_city_lang', 'city_id', 'language_id'),
    )
