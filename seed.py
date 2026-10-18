from dao import AuthorDao, GenreDao, ItemDao

def seed():
    author_dao = AuthorDao()
    genre_dao = GenreDao()
    item_dao = ItemDao()

    bulgakov = author_dao.insert("Михаил Булгаков")
    king = author_dao.insert("Стивен Кинг")
    
    fantasy = genre_dao.insert("Фантастика")
    horror = genre_dao.insert("Ужасы")

    i1 = item_dao.insert("Мастер и Маргарита", 1940, 10, 3)
    item_dao.link_author(i1, bulgakov)
    item_dao.link_genre(i1, fantasy)

    i2 = item_dao.insert("Оно", 1986, 9, 3)
    item_dao.link_author(i2, king)
    item_dao.link_genre(i2, horror)

    i3 = item_dao.insert("Непрочитанная книга", 2024, None, 1)
    item_dao.link_author(i3, king)
    item_dao.link_genre(i3, horror)

if __name__ == "__main__":
    seed()