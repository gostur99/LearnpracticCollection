"""Безопасное наполнение БД разнородными данными для проверки всех сценариев."""

from typing import Optional
from dao import ItemDao
from dataconn import get_connection, init_db


def get_or_create_author(fullname: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM authors WHERE fullname = ?;", (fullname,)
        ).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO authors (fullname) VALUES (?);", (fullname,)
        )
        conn.commit()
        return cursor.lastrowid


def get_or_create_genre(gname: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM genres WHERE gname = ?;", (gname,)
        ).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO genres (gname) VALUES (?);", (gname,)
        )
        conn.commit()
        return cursor.lastrowid


def get_or_create_item(
    name: str, year: int, rating: Optional[int], status_id: int
) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM items WHERE name = ? AND year = ?;", (name, year)
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE items SET rating = ?, status_id = ? WHERE id = ?;",
                (rating, status_id, row["id"]),
            )
            conn.commit()
            return row["id"]
        cursor = conn.execute(
            "INSERT INTO items (name, year, rating, status_id) VALUES (?, ?, ?,"
            " ?);",
            (name, year, rating, status_id),
        )
        conn.commit()
        return cursor.lastrowid


def seed():
    init_db()
    item_dao = ItemDao()

    # Авторы
    bulgakov = get_or_create_author("Михаил Булгаков")
    villeneuve = get_or_create_author("Дени Вильнёв")
    king = get_or_create_author("Стивен Кинг")
    sapkowski = get_or_create_author("Анджей Сапковский")
    cdpr = get_or_create_author("CD Projekt RED")
    marques = get_or_create_author("Гарсиа Маркес, Габриэль")

    # Жанры
    fantasy = get_or_create_genre("Фантастика")
    drama = get_or_create_genre("Драма")
    horror = get_or_create_genre("Ужасы")
    rpg = get_or_create_genre("RPG")
    novel = get_or_create_genre("Роман")

    # Произведения
    # 1. Завершено, 10
    i1 = get_or_create_item("Мастер и Маргарита", 1940, 10, 3)
    item_dao.link_author(i1, bulgakov)
    item_dao.link_genre(i1, novel)
    item_dao.link_genre(i1, drama)

    # 2. В планах, NULL
    i2 = get_or_create_item("Дюна: Часть вторая", 2024, None, 1)
    item_dao.link_author(i2, villeneuve)
    item_dao.link_genre(i2, fantasy)

    # 3. Завершено, 9
    i3 = get_or_create_item("Оно", 1986, 9, 3)
    item_dao.link_author(i3, king)
    item_dao.link_genre(i3, horror)

    # 4. В процессе, 8
    i4 = get_or_create_item("Ведьмак: Последнее желание", 1993, 8, 2)
    item_dao.link_author(i4, sapkowski)
    item_dao.link_genre(i4, fantasy)

    # 5. Завершено, 10 (Два автора!)
    i5 = get_or_create_item("Ведьмак 3: Дикая Охота", 2015, 10, 3)
    item_dao.link_author(i5, cdpr)
    item_dao.link_author(i5, sapkowski)
    item_dao.link_genre(i5, rpg)
    item_dao.link_genre(i5, fantasy)

    # 6. Брошено, 6
    i6 = get_or_create_item("Прибытие", 2016, 6, 4)
    item_dao.link_author(i6, villeneuve)
    item_dao.link_genre(i6, fantasy)

    # 7. Автор с запятой в имени
    i7 = get_or_create_item("Сто лет одиночества", 1967, 10, 3)
    item_dao.link_author(i7, marques)
    item_dao.link_genre(i7, novel)

    # 8. Тайтл со спецсимволом %
    i8 = get_or_create_item("100% Волк", 2020, 7, 3)
    item_dao.link_author(i8, 1)  # Заглушка 'Неизвестен'
    item_dao.link_genre(i8, 1)  # Заглушка 'Другое'


if __name__ == "__main__":
    seed()
    print("[SEED] База данных успешно заполнена тестовыми данными.")