from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

import re

from .books import ReturnedBook

__all__ = ['IncomingSeller', 'ReturnedSeller', 'ReturnedAllSellers', 'ReturnedSellerAndBooks']


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr

    @field_validator('first_name', 'last_name')
    @staticmethod
    def validate_field_length(val: str) -> str:
        if len(val) > 30:
            raise PydanticCustomError('Validation error', 'Value is too long!')
        return val

# Класс для валидации входящих данных.
class IncomingSeller(BaseSeller):
    password: str = Field(
        ...,
        min_length=8,
        max_length=256,
        examples=["SecurePass123!"],
        description='\n'.join([
            'Требования к паролю:',
            '8-256 символa',
            'Строчные и заглавные буквы',
            'Минимум одна цифра',
            'Без пробелов и кириллицы'
        ])
    )

    @field_validator("password")  # Валидатор, проверяет соблюдение требований к паролю
    @staticmethod
    def validate_password(val: str) -> str:
        if re.search(r'\s', val):
            raise PydanticCustomError('Validation error', 'Password cannot contain spaces!')
        if re.search(r'[а-яёА-ЯЁ]', val):
            raise PydanticCustomError('Validation error', 'Cyrillic letters are not allowed!')
        if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,256}$', val):
            raise PydanticCustomError('Validation error', 'Password must contain at least one lowercase letter, one uppercase letter and one digit!')
        WEAK_PASSWORDS = {'password123', 'qwerty123'}
        if val.lower() in WEAK_PASSWORDS:
            raise PydanticCustomError('Validation error', 'This password is too simple!')
        
        return val

# Класс, валидирующий исходящие данные.
class ReturnedSeller(BaseSeller):
    id: int

# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
    
# Класс для возврата массива объектов "Продавец и книги"
class ReturnedSellerAndBooks(ReturnedSeller):
    books: list[ReturnedBook]