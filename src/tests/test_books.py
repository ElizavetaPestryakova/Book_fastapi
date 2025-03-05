import pytest

from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller
from src.routers.v1.token import create_access_token



# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()

    book = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
    }

    token = create_access_token({"sub": seller.e_mail})

    response = await async_client.post("/api/v1/books/", json=book, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }


# Тест на ручку создающую слишком старую книгу
@pytest.mark.asyncio
async def test_create_book_with_old_year(db_session, async_client):
     
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()
    
    book = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
    }
    response = await async_client.post("/api/v1/books/", json=book)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = Book(author="Robert Martin", title="Clean Architecture", year=2025, pages=300)
    book_2 = Book(author="Entony Show", title="Inside CPYTHON", year=2023, pages=350)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert (len(response.json()["books"]) == 2)

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": "Clean Architecture",
                "author": "Robert Martin",
                "year": 2025,
                "id": book.id,
                "pages": 300,
            },
            {
                "title": "Inside CPYTHON",
                "author": "Entony Show",
                "year": 2023,
                "id": book_2.id,
                "pages": 350,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()
    
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = Book(author="Robert Martin", title="Clean Architecture", year=2025, pages=300)
    book_2 = Book(author="Entony Show", title="Inside CPYTHON", year=2023, pages=350)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "year": 2025,
        "id": book.id,
        "pages": 300,
        "seller_id": seller.id,
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()

    # Создаем книгу вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = Book(author="Robert Martin", title="Clean Architecture", year=2025, pages=300)

    db_session.add(book)
    await db_session.flush()

    update_book={
            "title": "Inside CPYTHON",
            "author": "Entony Show",
            "year": 2023,
            "id": book.id,
            "pages": 350,
            "seller_id": seller.id,
    }
    token = create_access_token({"sub": seller.e_mail})

    response = await async_client.put(
        f"/api/v1/books/{book.id}", json=update_book, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Book, book.id)
    assert res.title == "Inside CPYTHON"
    assert res.author == "Entony Show"
    assert res.year == 2023
    assert res.id == book.id
    assert res.pages == 350
    assert res.seller_id == seller.id


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()
    # Создаем книгу вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = Book(author="Entony Show", title="Inside CPYTHON", year=2023, pages=350)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


# Тест на ручку удаления книги с неправильным id
@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    
    seller = Seller(firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", password="Ivan123/")
    
    db_session.add(seller)
    await db_session.flush()

    # Создаем книгу вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = Book(author="Entony Show", title="Inside CPYTHON", year=2023, pages=350)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND