"""Набор консольных тестов для проверки всех требований ТЗ и Сценариев использования."""

from dao import AnalyticsDao, AuthorDao, GenreDao, ItemDao, StatusDao
from dataconn import reset_db
from seed import seed


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_crud_and_status():
    print_header("ТЕСТ 1: СТА ТУСЫ И БАЗОВЫЙ CRUD АВТОРОВ/ЖАНРОВ")

    status_dao = StatusDao()
    statuses = status_dao.get_all()
    print(">> Доступные статусы:")
    for s in statuses:
        print(f"  [{s.id}] {s.sname}")
    assert len(statuses) == 4, "Должно быть ровно 4 статуса!"

    author_dao = AuthorDao()
    new_author_id = author_dao.insert("Тестовый Режиссер")
    print(
        f"\n>> Добавлен автор с ID={new_author_id}:"
        f" {author_dao.get_by_id(new_author_id).fullname}"
    )

    author_dao.update(new_author_id, "Тестовый Режиссер (Изменен)")
    print(
        f">> Обновлен: {author_dao.get_by_id(new_author_id).fullname}"
    )

    author_dao.delete(new_author_id)
    print(f">> Удален? -> {author_dao.get_by_id(new_author_id) is None}")


def test_search_and_filter():
    print_header("ТЕСТ 2: ПОИСК, ФИЛЬТРАЦИЯ И СОРТИРОВКА (Сценарий 3)")
    item_dao = ItemDao()

    print("\n>> 1. Поиск по слову 'ведьмак' (case-insensitive):")
    results = item_dao.get_filtered(search_name="ведьмак")
    for item in results:
        print(
            f"  - {item.name} ({item.year}) | Авторы: {', '.join(item.authors)}"
        )
    assert len(results) == 2, "Должно быть найдено 2 тайтла о Ведьмаке!"

    print(
        "\n>> 2. Сортировка по оценке ASC (элементы с NULL обязаны быть в"
        " конце):"
    )
    all_items = item_dao.get_filtered(sort_by="rating", sort_desc=False)
    for item in all_items:
        r_str = item.rating if item.rating is not None else "NULL"
        print(f"  - {item.name:<30} | Оценка: {r_str}")
    assert (
        all_items[-1].rating is None
    ), "Элемент с оценкой NULL должен быть последним!"

    print("\n>> 3. Поиск со спецсимволом '100%':")
    spec_results = item_dao.get_filtered(search_name="100%")
    print(f"  Найдено: {[i.name for i in spec_results]}")
    assert len(spec_results) == 1 and spec_results[0].name == "100% Волк"


def test_analytics():
    print_header("ТЕСТ 3: АНАЛИТИКА И СТАТИСТИКА (Сценарий 4)")
    analytics_dao = AnalyticsDao()

    total, avg_rating = analytics_dao.get_general_stats()
    print(f">> Всего элементов: {total}")
    print(f">> Средняя оценка:  {avg_rating}")

    print("\n>> Распределение по 4 статусам:")
    for name, cnt in analytics_dao.get_status_distribution():
        print(f"  - [{name:<12}] : {cnt} шт.")

    print("\n>> Топ авторов по средней оценке:")
    top_authors = analytics_dao.get_top_authors()
    for rank, (name, rating, fin_cnt) in enumerate(top_authors, 1):
        print(
            f"  {rank}. {name:<30} | Средняя: {rating} | Завершено:"
            f" {fin_cnt}"
        )


def test_safe_delete_with_stub():
    print_header(
        "ТЕСТ 4: БЕЗОПАСНОЕ УДАЛЕНИЕ АВТОРА С ЗАМЕНОЙ НА 'НЕИЗВЕСТЕН' (Сценарий"
        " 5)"
    )
    author_dao = AuthorDao()
    item_dao = ItemDao()

    # Берем автора 'Михаил Булгаков' (он единственный у книги 'Мастер и Маргарита')
    bulgakov = next(
        a for a in author_dao.get_all() if a.fullname == "Михаил Булгаков"
    )
    print(
        f">> До удаления: Книга 'Мастер и Маргарита' связана с автором:"
        f" {item_dao.get_filtered(search_name='Мастер')[0].authors}"
    )

    print(
        f">> Выполняем безопасное удаление автора '{bulgakov.fullname}' (ID"
        f"={bulgakov.id})..."
    )
    author_dao.delete(bulgakov.id, stub_id=1)

    master_item = item_dao.get_filtered(search_name="Мастер")[0]
    print(f">> После удаления: Книга осталась в базе!")
    print(f"  Новый автор книги: {master_item.authors}")
    assert (
        master_item.authors[0] == "Неизвестен"
    ), "Автор должен был замениться на 'Неизвестен'!"


def main():
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  ПРОВОДИТСЯ ТЕСТИРОВАНИЕ DAO-СЛОЯ КАТАЛОГИЗАТОРА (000)          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    reset_db()
    seed()

    test_crud_and_status()
    test_search_and_filter()
    test_analytics()
    test_safe_delete_with_stub()

    print(
        "\n[УСПЕХ] Все консольные тесты пройдены! DAO-слой работает"
        " корректно.\n"
    )


if __name__ == "__main__":
    main()