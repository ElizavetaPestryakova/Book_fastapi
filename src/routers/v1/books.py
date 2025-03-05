from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations import get_async_session
from src.models.books import Book
from src.routers.v1.token import valid_user_token
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook, TokenData

books_router = APIRouter(tags=["books"], prefix="/books")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@books_router.post(
    "/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_book(
    book: IncomingBook,
    session: DBSession,
    token: Annotated[TokenData, Depends(valid_user_token)]
):
    new_book = Book(
        **{
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "pages": book.pages,
        }
    )

    session.add(new_book)
    await session.flush()

    return new_book


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    query = select(Book)  # SELECT * FROM book
    result = await session.execute(query)
    books = result.scalars().all()
    return {"books": books}


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    if result := await session.get(Book, book_id):
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook, session: DBSession, token: Annotated[TokenData, Depends(valid_user_token)]):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_book_data.author
        updated_book.title = new_book_data.title
        updated_book.year = new_book_data.year
        updated_book.pages = new_book_data.pages

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)