from typing import List, Optional
from database import get_connection
from models import Status

class StatusDao:
    def get_all(self) -> List[Status]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, sname FROM statuses ORDER BY id ASC;").fetchall()
            return [Status(id=r["id"], sname=r["sname"]) for r in rows]

    def get_by_id(self, status_id: int) -> Optional[Status]:
        with get_connection() as conn:
            row = conn.execute("SELECT id, sname FROM statuses WHERE id = ?;", (status_id,)).fetchone()
            return Status(id=row["id"], sname=row["sname"]) if row else None
class AuthorDao:
    def get_all(self) -> List[Author]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, fullname FROM authors ORDER BY fullname ASC;").fetchall()
            return [Author(id=r["id"], fullname=r["fullname"]) for r in rows]

    def get_by_id(self, author_id: int) -> Optional[Author]:
        with get_connection() as conn:
            row = conn.execute("SELECT id, fullname FROM authors WHERE id = ?;", (author_id,)).fetchone()
            return Author(id=row["id"], fullname=row["fullname"]) if row else None

    def insert(self, fullname: str) -> int:
        with get_connection() as conn:
            cursor = conn.execute("INSERT INTO authors (fullname) VALUES (?);", (fullname,))
            conn.commit()
            return cursor.lastrowid

    def update(self, author_id: int, fullname: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("UPDATE authors SET fullname = ? WHERE id = ?;", (fullname, author_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, author_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM authors WHERE id = ?;", (author_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count_links(self, author_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM item_authors WHERE author_id = ?;", (author_id,)).fetchone()
            return row["cnt"]
class GenreDao:
    def get_all(self) -> List[Genre]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, gname FROM genres ORDER BY gname ASC;").fetchall()
            return [Genre(id=r["id"], gname=r["gname"]) for r in rows]

    def get_by_id(self, genre_id: int) -> Optional[Genre]:
        with get_connection() as conn:
            row = conn.execute("SELECT id, gname FROM genres WHERE id = ?;", (genre_id,)).fetchone()
            return Genre(id=row["id"], gname=row["gname"]) if row else None

    def insert(self, gname: str) -> int:
        with get_connection() as conn:
            cursor = conn.execute("INSERT INTO genres (gname) VALUES (?);", (gname,))
            conn.commit()
            return cursor.lastrowid

    def update(self, genre_id: int, gname: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("UPDATE genres SET gname = ? WHERE id = ?;", (gname, genre_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, genre_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM genres WHERE id = ?;", (genre_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count_links(self, genre_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM item_genres WHERE genre_id = ?;", (genre_id,)).fetchone()
            return row["cnt"]
from typing import List, Optional
from database import get_connection
from models import Item, ItemFull

def _escape_like(text: str) -> str:
    """Безопасное экранирование служебных символов для LIKE запроса."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

class ItemDao:
    def get_by_id(self, item_id: int) -> Optional[Item]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, name, year, rating, status_id FROM items WHERE id = ?;", (item_id,)
            ).fetchone()
            if not row: return None
            return Item(id=row["id"], name=row["name"], year=row["year"], rating=row["rating"], status_id=row["status_id"])

    def insert(self, name: str, year: int, rating: Optional[int], status_id: int) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (name, year, rating, status_id) VALUES (?, ?, ?, ?);",
                (name, year, rating, status_id)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, item_id: int, name: str, year: int, rating: Optional[int], status_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE items SET name = ?, year = ?, rating = ?, status_id = ? WHERE id = ?;",
                (name, year, rating, status_id, item_id)
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
            conn.execute("INSERT OR IGNORE INTO item_authors (item_id, author_id) VALUES (?, ?);", (item_id, author_id))
            conn.commit()

    def link_genre(self, item_id: int, genre_id: int) -> None:
        with get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO item_genres (item_id, genre_id) VALUES (?, ?);", (item_id, genre_id))
            conn.commit()

    def clear_authors(self, item_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM item_authors WHERE item_id = ?;", (item_id,))
            conn.commit()

    def clear_genres(self, item_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM item_genres WHERE item_id = ?;", (item_id,))
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
        # Безопасный выбор поля сортировки
        allowed_sort = {"name": "i.name", "year": "i.year", "rating": "i.rating"}
        order_field = allowed_sort.get(sort_by, "i.name")
        order_direction = "DESC" if sort_desc else "ASC"

        # Фикс для элементов без оценки (NULL) — всегда в конце списка
        nulls_order = "i.rating IS NULL ASC, " if sort_by == "rating" else ""

        sql = f"""
            SELECT
                i.id,
                i.name,
                i.year,
                i.rating,
                s.sname AS status_name,
                GROUP_CONCAT(DISTINCT a.fullname, '|||') AS authors_list,
                GROUP_CONCAT(DISTINCT g.gname, '|||') AS genres_list
            FROM items i
            JOIN statuses s ON i.status_id = s.id
            LEFT JOIN item_authors ia ON i.id = ia.item_id
            LEFT JOIN authors a ON ia.author_id = a.id
            LEFT JOIN item_genres ig ON i.id = ig.item_id
            LEFT JOIN genres g ON ig.genre_id = g.id
            WHERE
                (:search IS NULL OR LOWER(i.name) LIKE LOWER(:search_like) ESCAPE '\\')
                AND (:genre_id IS NULL OR i.id IN (SELECT item_id FROM item_genres WHERE genre_id = :genre_id))
                AND (:author_id IS NULL OR i.id IN (SELECT item_id FROM item_authors WHERE author_id = :author_id))
                AND (:status_id IS NULL OR i.status_id = :status_id)
                AND (:year IS NULL OR i.year = :year)
            GROUP BY i.id
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
                    authors=r["authors_list"].split("|||") if r["authors_list"] else [],
                    genres=r["genres_list"].split("|||") if r["genres_list"] else [],
                )
                for r in rows
            ]
class AnalyticsDao:
    def get_general_stats(self) -> Tuple[int, float]:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(id) AS total, ROUND(COALESCE(AVG(rating), 0), 1) AS avg_rating FROM items;
            """).fetchone()
            return row["total"], row["avg_rating"]

    def get_status_distribution(self) -> List[Tuple[str, int]]:
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
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT a.fullname AS name, ROUND(AVG(i.rating), 1) AS avg_rating, COUNT(i.id) AS cnt
                FROM authors a
                JOIN item_authors ia ON a.id = ia.author_id
                JOIN items i ON ia.item_id = i.id
                WHERE i.rating IS NOT NULL
                GROUP BY a.id, a.fullname
                ORDER BY avg_rating DESC, cnt DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [(r["name"], r["avg_rating"], r["cnt"]) for r in rows]

    def get_top_genres(self, limit: int = 10) -> List[Tuple[str, float, int]]:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT g.gname AS name, ROUND(AVG(i.rating), 1) AS avg_rating, COUNT(i.id) AS cnt
                FROM genres g
                JOIN item_genres ig ON g.id = ig.genre_id
                JOIN items i ON ig.item_id = i.id
                WHERE i.rating IS NOT NULL
                GROUP BY g.id, g.gname
                ORDER BY avg_rating DESC, cnt DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [(r["name"], r["avg_rating"], r["cnt"]) for r in rows]