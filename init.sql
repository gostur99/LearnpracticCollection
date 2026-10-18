PRAGMA foreign_keys = ON;

1. Справочник статусов (Системный справочник, нередактируемый из UI)
CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sname TEXT NOT NULL UNIQUE CHECK(length(trim(sname)) > 0)
);

2. Справочник авторов / режиссёров / разработчиков
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL UNIQUE CHECK(length(trim(fullname)) > 0)
);

3. Справочник жанров
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gname TEXT NOT NULL UNIQUE CHECK(length(trim(gname)) > 0)
);

4. Основная таблица элементов коллекции (книги / фильмы / игры)
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    year INTEGER NOT NULL CHECK(year >= 1800 AND year <= 2100),
    rating INTEGER CHECK(rating IS NULL OR (rating >= 1 AND rating <= 10)),
    status_id INTEGER NOT NULL,
    -- Статус удалять нельзя (системный справочник)
    FOREIGN KEY (status_id) REFERENCES statuses(id) ON DELETE RESTRICT
);

5. Связующая таблица: Элементы <-> Авторы
CREATE TABLE IF NOT EXISTS item_authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    -- Запрет дублирования связи один автор + один элемент
    UNIQUE(item_id, author_id),
    -- При удалении элемента удаляется связь
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    -- При удалении автора (с подтверждением пользователя) удаляется связь, элемент остается
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

6. Связующая таблица: Элементы <-> Жанры (M:N)
CREATE TABLE IF NOT EXISTS item_genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    -- Запрет дублирования связи один жанр + один элемент
    UNIQUE(item_id, genre_id),
    -- При удалении элемента удаляется связь
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    -- При удалении жанра (с подтверждением пользователя) удаляется связь, элемент остается
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

ИНДЕКСЫ
CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_items_year ON items(year);
CREATE INDEX IF NOT EXISTS idx_items_rating ON items(rating);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status_id);
CREATE INDEX IF NOT EXISTS idx_item_authors_author ON item_authors(author_id);
CREATE INDEX IF NOT EXISTS idx_item_genres_genre ON item_genres(genre_id);

НАЧАЛЬНЫЕ СИСТЕМНЫЕ ДАННЫЕ

INSERT OR IGNORE INTO statuses (id, sname) VALUES
    (1, 'В планах'),
    (2, 'В процессе'),
    (3, 'Завершено'),
    (4, 'Брошено');

INSERT OR IGNORE INTO authors (id, fullname) VALUES
    (1, 'Неизвестен'),
    (2, 'Народное творчество');

INSERT OR IGNORE INTO genres (id, gname) VALUES
    (1, 'Другое');
