# main.py — головний файл програми, запускати його

from config import load_config
from storage import load_data, save_data
from commands import (add_transaction, display_transactions,
                      delete_transaction, edit_transaction,
                      search_by_tag, manage_categories, choose_from_list)
from charts import show_pie_chart


def show_balance(data):
    # Показує поточний баланс гаманця
    wallet = data["wallet"]
    print(f"\nГаманець '{wallet['name']}': {wallet['balance']:.2f} грн")


def main():
    # Завантажуємо налаштування і дані
    config = load_config()
    filename = config["data_file"]
    data = load_data(filename)

    # Головний цикл програми — працює поки користувач не вийде
    while True:
        print("=" * 40)
        show_balance(data)
        print("=" * 40)
        action = choose_from_list([
            "Додати витрату",
            "Додати дохід",
            "Переглянути транзакції",
            "Видалити транзакцію",
            "Редагувати транзакцію",
            "Пошук за тегом",
            "Управління категоріями",
            "Діаграма витрат",
            "Вийти"
        ], "\nОберіть дію:")

        if action == "Додати витрату":
            add_transaction(data, filename, "expense")

        elif action == "Додати дохід":
            add_transaction(data, filename, "income")

        elif action == "Переглянути транзакції":
            display_transactions(data, config)

        elif action == "Видалити транзакцію":
            delete_transaction(data, filename)

        elif action == "Редагувати транзакцію":
            edit_transaction(data, filename)

        elif action == "Пошук за тегом":
            search_by_tag(data)

        elif action == "Управління категоріями":
            manage_categories(data, filename)

        elif action == "Діаграма витрат":
            show_pie_chart(data)

        elif action == "Вийти":
            print("\nДо побачення!")
            break


if __name__ == "__main__":
    # __name__ == "__main__" означає що цей блок виконується
    # тільки коли запускаємо файл напряму (python main.py)
    # але не коли імпортуємо його в інший файл
    main()
