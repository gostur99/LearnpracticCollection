from database import reset_db
from seed_data import seed
from dao import StatusDao, AuthorDao, GenreDao, ItemDao, AnalyticsDao

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_items_filter():
    print_header("ТЕСТ 1: ПОИСК И СОРТИРОВКА (ItemDao)")
    dao = ItemDao()
    print("\n>> Сортировка по оценке ASC (NULL должен быть в самом конце!):")
    for item in dao.get_filtered(sort_by="rating", sort_desc=False):
        rating = item.rating if item.rating is not None else "NULL"
        print(f"  - {item.name} | Оценка: {rating}")

def test_cascade_delete():
    print_header("ТЕСТ 2: БЕЗОПАСНОЕ УДАЛЕНИЕ АВТОРА (CASCADE)")
    author_dao = AuthorDao()
    item_dao = ItemDao()

    all_authors = author_dao.get_all()
    king = next((a for a in all_authors if a.fullname == "Стивен Кинг"), None)
    
    cnt = author_dao.count_links(king.id)
    print(f"\n>> У автора '{king.fullname}' привязано произведений: {cnt}")
    print(">> Удаляем автора...")
    author_dao.delete(king.id)
    print(f"  Автор удален: {author_dao.get_by_id(king.id) is None}")

    print("\n>> Книга 'Оно' должна остаться в коллекции:")
    for item in item_dao.get_filtered(search_name="Оно"):
        print(f"  - {item.name} | Авторы: {item.authors}")

def test_edge_cases():
    print_header("ТЕСТ 3: ПРОВЕРКА КРАЕВЫХ СЛУЧАЕВ (Запятые и экранирование)")
    author_dao = AuthorDao()
    item_dao = ItemDao()

    complex_author = "Гарсиа Маркес, Габриэль"
    a_id = author_dao.insert(complex_author)
    
    item_id = item_dao.insert("Сто лет одиночества", 1967, 10, 3)
    item_dao.link_author(item_id, a_id)

    items = item_dao.get_filtered(search_name="Сто лет одиночества")
    print(f"\n>> Книга с автором '{complex_author}':")
    print(f"  Авторы в списке: {items[0].authors}")
    assert len(items[0].authors) == 1, "Имя автора разорвалось!"
    print("  [OK] Разделитель '|||' отработал идеально!")

    item_dao.insert("100% Волк", 2020, 7, 3)
    results = item_dao.get_filtered(search_name="100%")
    print(f"\n>> Поиск со спецсимволом '100%':")
    print(f"  Найдено: {[i.name for i in results]}")
    assert len(results) == 1, "Экранирование сломалось!"
    print("  [OK] Экранирование LIKE отработало идеально!")

def main():
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  ТЕСТИРОВАНИЕ DAO-СЛОЯ: Каталогизатор личной коллекции (000)    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    reset_db()
    seed()

    test_items_filter()
    test_cascade_delete()
    test_edge_cases()

    print("\n[OK] Все тесты успешно завершены!\n")

if __name__ == "__main__":
    main()