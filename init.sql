PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sname TEXT NOT NULL UNIQUE CHECK(length(trim(sname)) > 0)
);

CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL UNIQUE CHECK(length(trim(fullname)) > 0)
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gname TEXT NOT NULL UNIQUE CHECK(length(trim(gname)) > 0)
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    year INTEGER NOT NULL CHECK(year >= 1800 AND year <= 2100),
    rating INTEGER CHECK(rating IS NULL OR (rating >= 1 AND rating <= 10)),
    status_id INTEGER NOT NULL,
    FOREIGN KEY (status_id) REFERENCES statuses(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS item_authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    UNIQUE(item_id, author_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS item_genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    UNIQUE(item_id, genre_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_items_year ON items(year);
CREATE INDEX IF NOT EXISTS idx_items_rating ON items(rating);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status_id);
CREATE INDEX IF NOT EXISTS idx_item_authors_author ON item_authors(author_id);
CREATE INDEX IF NOT EXISTS idx_item_genres_genre ON item_genres(genre_id);

INSERT OR IGNORE INTO statuses (id, sname) VALUES
    (1, 'В планах'), (2, 'В процессе'), (3, 'Завершено'), (4, 'Брошено');

INSERT OR IGNORE INTO authors (id, fullname) VALUES
    (1, 'Неизвестен'), (2, 'Народное творчество');

INSERT OR IGNORE INTO genres (id, gname) VALUES
    (1, 'Другое');