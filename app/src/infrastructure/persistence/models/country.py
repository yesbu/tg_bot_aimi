from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .city import City
    from .language import Language

class Country(Base):
    __tablename__ = "countries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)
    
    translations: Mapped[list["CountryTranslation"]] = relationship(
        back_populates="country",
        cascade="all, delete-orphan"
    )
    cities: Mapped[list["City"]] = relationship(back_populates="country")
    
    def __repr__(self):
        return f"<Country(code={self.code})>"


class CountryTranslation(Base):
    __tablename__ = "country_translations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    country: Mapped["Country"] = relationship(back_populates="translations")
    language: Mapped["Language"] = relationship()
    
    __table_args__ = (
        UniqueConstraint('country_id', 'language_id', name='uq_country_language'),
        Index('idx_country_lang', 'country_id', 'language_id'),
    )
    
    def __repr__(self):
        return f"<CountryTranslation(country_id={self.country_id}, lang={self.language_id}, name={self.name})>"