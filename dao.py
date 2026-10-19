"""Слой доступа к данным (DAO) для всех сущностей и аналитики."""

from typing import List, Optional, Tuple
from dataconn import get_connection
from models import Author, Genre, Item, ItemFull, Status


def _escape_like(text: str) -> str:
    """Экранирование служебных символов SQLite для оператора LIKE."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class StatusDao:

    def get_all(self) -> List[Status]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, sname FROM statuses ORDER BY id ASC;"
            ).fetchall()
            return [Status(id=r["id"], sname=r["sname"]) for r in rows]

    def get_by_id(self, status_id: int) -> Optional[Status]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, sname FROM statuses WHERE id = ?;", (status_id,)
            ).fetchone()
            return Status(id=row["id"], sname=row["sname"]) if row else None


class AuthorDao:

    def get_all(self) -> List[Author]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, fullname FROM authors ORDER BY fullname ASC;"
            ).fetchall()
            return [Author(id=r["id"], fullname=r["fullname"]) for r in rows]

    def get_by_id(self, author_id: int) -> Optional[Author]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, fullname FROM authors WHERE id = ?;", (author_id,)
            ).fetchone()
            return (
                Author(id=row["id"], fullname=row["fullname"]) if row else None
            )

    def insert(self, fullname: str) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO authors (fullname) VALUES (?);", (fullname,)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, author_id: int, fullname: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE authors SET fullname = ? WHERE id = ?;",
                (fullname, author_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, author_id: int, stub_id: Optional[int] = None) -> bool:
        """Удаляет автора.

        Если передан stub_id — выполняет безопасное удаление с перепривязкой
        единственных авторов на заглушку.
        """
        if stub_id is not None:
            return self.delete_safe(author_id, stub_id=stub_id)

        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM authors WHERE id = ?;", (author_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_safe(self, author_id: int, stub_id: int = 1) -> bool:
        """Безопасное удаление автора (Сценарий 5).

        Если у произведения этот автор был единственным, перепривязывает к
        заглушке 'Неизвестен' (stub_id=1).
        """
        if author_id == stub_id:
            return False  # Запрет удаления системной заглушки

        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO item_authors (item_id, author_id)
                SELECT item_id, ?
                FROM item_authors
                WHERE author_id = ?
                  AND item_id IN (
                      SELECT item_id FROM item_authors
                      GROUP BY item_id HAVING COUNT(author_id) = 1
                  );
            """,
                (stub_id, author_id),
            )

            cursor = conn.execute(
                "DELETE FROM authors WHERE id = ?;", (author_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def count_links(self, author_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM item_authors WHERE author_id = ?;",
                (author_id,),
            ).fetchone()
            return row["cnt"]


class GenreDao:

    def get_all(self) -> List[Genre]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, gname FROM genres ORDER BY gname ASC;"
            ).fetchall()
            return [Genre(id=r["id"], gname=r["gname"]) for r in rows]

    def get_by_id(self, genre_id: int) -> Optional[Genre]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, gname FROM genres WHERE id = ?;", (genre_id,)
            ).fetchone()
            return Genre(id=row["id"], gname=row["gname"]) if row else None

    def insert(self, gname: str) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO genres (gname) VALUES (?);", (gname,)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, genre_id: int, gname: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE genres SET gname = ? WHERE id = ?;", (gname, genre_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, genre_id: int, stub_id: Optional[int] = None) -> bool:
        if stub_id is not None:
            return self.delete_safe(genre_id, stub_id=stub_id)

        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM genres WHERE id = ?;", (genre_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_safe(self, genre_id: int, stub_id: int = 1) -> bool:
        if genre_id == stub_id:
            return False

        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO item_genres (item_id, genre_id)
                SELECT item_id, ?
                FROM item_genres
                WHERE genre_id = ?
                  AND item_id IN (
                      SELECT item_id FROM item_genres
                      GROUP BY item_id HAVING COUNT(genre_id) = 1
                  );
            """,
                (stub_id, genre_id),
            )

            cursor = conn.execute(
                "DELETE FROM genres WHERE id = ?;", (genre_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def count_links(self, genre_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM item_genres WHERE genre_id = ?;",
                (genre_id,),
            ).fetchone()
            return row["cnt"]

class ItemDao:

    def get_by_id(self, item_id: int) -> Optional[Item]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, name, year, rating, status_id FROM items WHERE id"
                " = ?;",
                (item_id,),
            ).fetchone()
            if not row:
                return None
            return Item(
                id=row["id"],
                name=row["name"],
                year=row["year"],
                rating=row["rating"],
                status_id=row["status_id"],
            )

    def insert(
        self, name: str, year: int, rating: Optional[int], status_id: int
    ) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (name, year, rating, status_id) VALUES (?, ?,"
                " ?, ?);",
                (name, year, rating, status_id),
            )
            conn.commit()
            return cursor.lastrowid

    def update(
        self,
        item_id: int,
        name: str,
        year: int,
        rating: Optional[int],
        status_id: int,
    ) -> bool:
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE items SET name = ?, year = ?, rating = ?, status_id = ?"
                " WHERE id = ?;",
                (name, year, rating, status_id, item_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, item_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM items WHERE id = ?;", (item_id,))
            conn.commit()
            return cursor.rowcount > 0

    def link_author(self, item_id: int, author_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO item_authors (item_id, author_id)"
                " VALUES (?, ?);",
                (item_id, author_id),
            )
            conn.commit()

    def link_genre(self, item_id: int, genre_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO item_genres (item_id, genre_id) VALUES"
                " (?, ?);",
                (item_id, genre_id),
            )
            conn.commit()

    def clear_authors(self, item_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM item_authors WHERE item_id = ?;", (item_id,)
            )
            conn.commit()

    def clear_genres(self, item_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM item_genres WHERE item_id = ?;", (item_id,)
            )
            conn.commit()

    def get_filtered(
        self,
        search_name: Optional[str] = None,
        genre_id: Optional[int] = None,
        author_id: Optional[int] = None,
        status_id: Optional[int] = None,
        year: Optional[int] = None,
        sort_by: str = "name",
        sort_desc: bool = False,
    ) -> List[ItemFull]:
        allowed_sort = {
            "name": "i.name",
            "year": "i.year",
            "rating": "i.rating",
        }
        order_field = allowed_sort.get(sort_by, "i.name")
        order_direction = "DESC" if sort_desc else "ASC"

        # NULL значения оценок выводятся в самом конце
        nulls_order = "i.rating IS NULL ASC, " if sort_by == "rating" else ""

        sql = f"""
            SELECT
                i.id,
                i.name,
                i.year,
                i.rating,
                s.sname AS status_name,
                (
                    SELECT GROUP_CONCAT(a.fullname, '|||')
                    FROM item_authors ia
                    JOIN authors a ON ia.author_id = a.id
                    WHERE ia.item_id = i.id
                ) AS authors_list,
                (
                    SELECT GROUP_CONCAT(g.gname, '|||')
                    FROM item_genres ig
                    JOIN genres g ON ig.genre_id = g.id
                    WHERE ig.item_id = i.id
                ) AS genres_list
            FROM items i
            JOIN statuses s ON i.status_id = s.id
            WHERE
                (:search IS NULL OR LOWER(i.name) LIKE LOWER(:search_like) ESCAPE '\\')
                AND (:genre_id IS NULL OR i.id IN (SELECT item_id FROM item_genres WHERE genre_id = :genre_id))
                AND (:author_id IS NULL OR i.id IN (SELECT item_id FROM item_authors WHERE author_id = :author_id))
                AND (:status_id IS NULL OR i.status_id = :status_id)
                AND (:year IS NULL OR i.year = :year)
            ORDER BY {nulls_order}{order_field} {order_direction};
        """

        escaped_search = _escape_like(search_name) if search_name else None
        params = {
            "search": search_name,
            "search_like": f"%{escaped_search}%" if escaped_search else None,
            "genre_id": genre_id,
            "author_id": author_id,
            "status_id": status_id,
            "year": year,
        }

        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [
                ItemFull(
                    id=r["id"],
                    name=r["name"],
                    year=r["year"],
                    rating=r["rating"],
                    status_name=r["status_name"],
                    authors=(
                        r["authors_list"].split("|||")
                        if r["authors_list"]
                        else []
                    ),
                    genres=(
                        r["genres_list"].split("|||")
                        if r["genres_list"]
                        else []
                    ),
                )
                for r in rows
            ]


class AnalyticsDao:

    def get_general_stats(self) -> Tuple[int, float]:
        """Расчет общего числа элементов и средней оценки."""
        with get_connection() as conn:
            row = conn.execute("""
                SELECT 
                    COUNT(id) AS total, 
                    ROUND(COALESCE(AVG(rating), 0.0), 1) AS avg_rating 
                FROM items;
            """).fetchone()
            return row["total"], row["avg_rating"]

    def get_status_distribution(self) -> List[Tuple[str, int]]:
        """Распределение элементов по всем 4 статусам."""
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT s.sname AS name, COUNT(i.id) AS cnt
                FROM statuses s
                LEFT JOIN items i ON s.id = i.status_id
                GROUP BY s.id, s.sname
                ORDER BY s.id ASC;
            """).fetchall()
            return [(r["name"], r["cnt"]) for r in rows]

    def get_top_authors(self, limit: int = 10) -> List[Tuple[str, float, int]]:
        """Топ-10 авторов.

        Сортировка по AVG(rating) (только оценочные элементы). Tie-breaker:
        число завершенных произведений (status_id = 3).
        """
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT 
                    a.fullname AS name, 
                    ROUND(AVG(i.rating), 1) AS avg_rating, 
                    COUNT(CASE WHEN i.status_id = 3 THEN 1 END) AS finished_count
                FROM authors a
                JOIN item_authors ia ON a.id = ia.author_id
                JOIN items i ON ia.item_id = i.id
                WHERE i.rating IS NOT NULL
                GROUP BY a.id, a.fullname
                ORDER BY avg_rating DESC, finished_count DESC
                LIMIT ?;
            """,
                (limit,),
            ).fetchall()
            return [(r["name"], r["avg_rating"], r["finished_count"]) for r in rows]

    def get_top_genres(self, limit: int = 10) -> List[Tuple[str, float, int]]:
        """Топ-10 жанров с аналогичным алгоритмом расчета."""
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT 
                    g.gname AS name, 
                    ROUND(AVG(i.rating), 1) AS avg_rating, 
                    COUNT(CASE WHEN i.status_id = 3 THEN 1 END) AS finished_count
                FROM genres g
                JOIN item_genres ig ON g.id = ig.genre_id
                JOIN items i ON ig.item_id = i.id
                WHERE i.rating IS NOT NULL
                GROUP BY g.id, g.gname
                ORDER BY avg_rating DESC, finished_count DESC
                LIMIT ?;
            """,
                (limit,),
            ).fetchall()
            return [(r["name"], r["avg_rating"], r["finished_count"]) for r in rows]