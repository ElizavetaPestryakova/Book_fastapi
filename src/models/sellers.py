from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .books import Book

class Seller(BaseModel):
    __tablename__ = 'sellers_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    e_mail: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String(256), nullable=False)
    books = relationship(argument='Book', back_populates='seller', cascade='all, delete-orphan')