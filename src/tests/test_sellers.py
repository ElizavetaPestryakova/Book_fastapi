import pytest

from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller
from src.routers.v1.token import create_access_token


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "firs_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "Ivan@Ivanov.com",
        "password": "Ivan123/",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    assert result_data["first_name"] == "Ivan"
    assert result_data["last_name"] == "Ivanov"
    assert result_data["e_mail"] == "Ivan@Ivanov.com"


# Тест на дублирующую электронную почту
@pytest.mark.asyncio
async def test_create_seller_with_duplicate_email(async_client):
    data = {
        "firs_name": "Nikita",
        "last_name": "Kuzin",
        "e_mail": "Ivan@Ivanov.com",
        "password": "Nikita123/",
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.jsom() == {
        "detail": "Email already registered!",
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = Seller(
        firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", hash_password="Ivan123/"
    )
    seller_2 = Seller(
        firs_name="Nikita", last_name="Kuzin", e_mail="Nikita@Kuzin.com", hash_password="Nikita123/"
    )
    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert (len(response.json()["sellers"]) == 2)

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "e_mail": "Ivan@Ivanov.com",
                "id": seller.id,
            },
            {
                "first_name": "Nikita",
                "last_name": "Kuzin",
                "e_mail": "Nikita@Kuzin.com",
                "id": seller_2.id,
            },
        ]
    }


# Тест на ручку получения одного продавца и его книг
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = Seller(
        firs_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.com", hash_password="Ivan123/"
    )
    seller_2 = Seller(
        firs_name="Nikita", last_name="Kuzin", e_mail="Nikita@Kuzin.com", hash_password="Nikita123/"
    )
    db_session.add_all([seller, seller_2])
    await db_session.flush()

    book = Book(author="Robert Martin", title="Clean Architecture", year=2025, pages=300)

    db_session.add(book)
    await db_session.flush()

    token = create_access_token({"sub": seller.email})
    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": seller.id,
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "Ivan@Ivanov.com",
        "books": [
            {
                "id": book.id,
                "author": "Robert Martin",
                "title": "Clean Architecture",
                "year": 2025,
                "count_pages": 300,
                "seller_id": seller.id,
            }
        ],
    }


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.ocm")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "first_name": "Maxim",
            "last_name": "Maximov",
            "e_mail": "Ivan@Ivanov.com",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.title == "Maxim"
    assert res.author == "Maximov"
    assert res.e_mail == "Ivan@Ivanov.com"
    assert res.id == seller.id


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.ocm")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


# Тест на ручку удаления продавца с неправильным id
@pytest.mark.asyncio
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="Ivan@Ivanov.ocm")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND