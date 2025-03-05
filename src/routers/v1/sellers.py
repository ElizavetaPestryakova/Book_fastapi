from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations import get_async_session
from src.models.sellers import Seller
from src.routers.v1.token import pwd_context, valid_user_token
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSellerAndBooks, ReturnedSeller, TokenData

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Ручка, регистрирующая продавца
@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "e_mail": seller.e_mail,
            "hash_password": pwd_context.hash(seller.password),
        }
    )

    session.add(new_seller)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerAndBooks)
async def get_seller(seller_id: int, session: DBSession, token: Annotated[TokenData, Depends(valid_user_token)]):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)

    if seller := result.scalars().first():
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: ReturnedSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.e_mail = new_seller_data.e_mail

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)