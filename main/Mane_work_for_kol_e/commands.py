# commands.py — всі команди програми (взаємодія з користувачем через input)

from datetime import datetime
from models import Transaction, Wallet
from storage import (save_data, get_all_categories,
                     get_all_tags, update_tags, DEFAULT_CATEGORIES)


def get_current_date():
    # Повертає сьогоднішню дату у форматі "2024-01-25"
    return datetime.now().strftime("%d.%m.%Y")


def choose_from_list(items, prompt):
    # Показує список і просить вибрати один елемент
    # Використовується для вибору категорії, тегу тощо
    print(prompt)
    for i, item in enumerate(items, 1):
        # enumerate дає нам індекс і значення одночасно
        print(f"  {i}. {item}")
    while True:
        choice = input("Ваш вибір (номер): ").strip() #strip це пробіли
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return items[int(choice) - 1]
        print("Невірний вибір, спробуйте ще раз")


def input_amount():
    # Просить ввести суму і перевіряє що це число
    while True:
        amount = input("Сума (грн): ").strip()
        try:
            value = float(amount)
            if value <= 0:
                print("Сума повинна бути більше 0")
                continue
            return value
        except ValueError:
            # ValueError виникає коли float() не може перетворити рядок
            print("Введіть числове значення")
    
def input_date():
    while True:
        date_input = input(f"Дата (або Enter = сьогодні {get_current_date()}): ").strip()

        if not date_input:
            return get_current_date()

        try:
            datetime.strptime(date_input, "%d.%m.%Y")  # strptime — перевіряє що рядок відповідає формату
            return date_input
        except ValueError:
            print("Невірний формат! Спробуй ще раз (ДД.ММ.РРРР)")
            continue


def input_tags(data):
    # Дозволяє вибрати існуючі теги або ввести нові (до 5 штук)
    existing_tags = get_all_tags(data)
    selected_tags = []

    print("Теги (до 5 штук, Enter щоб пропустити)")
    if existing_tags:
        print(f"Існуючі теги: {', '.join(existing_tags)}")

    for i in range(5):
        tag = input(f"Тег {i+1} (або Enter щоб завершити): ").strip()
        if not tag:
            break
        selected_tags.append(tag)

    return selected_tags


def generate_id(data):
    # Генерує унікальний ID для нової транзакції
    transactions = data.get("transactions", [])
    if not transactions:
        return 1
    # Бере максимальний існуючий ID і додає 1
    return max(t["id"] for t in transactions) + 1


# ============================================================
# ДОДАВАННЯ ТРАНЗАКЦІЙ
# ============================================================

def add_transaction(data, filename, trans_type):
    # Додає нову витрату або дохід
    # trans_type = "expense" або "income"

    print("\n" + "="*40)
    print("Додавання витрати" if trans_type == "expense" else "Додавання доходу")
    print("="*40)

    # Вибір категорії
    categories = get_all_categories(data, trans_type)
    category = choose_from_list(categories, "Оберіть категорію:")

    # Введення суми
    amount = input_amount()

    # Введення дати
    date = input_date()

    # Введення тегів
    tags = input_tags(data)

    # Введення коментаря
    comment = input("Коментар (необов'язково): ").strip()

    # Створюємо об'єкт транзакції
    transaction = Transaction(
        id=generate_id(data),
        trans_type=trans_type,
        amount=amount,
        category=category,
        date=date,
        tags=tags,
        comment=comment
    )

    # Оновлюємо баланс гаманця
    wallet = Wallet.from_dict(data["wallet"])
    if trans_type == "expense":
        result = wallet.withdraw(amount)
        if not result:
            return  # якщо недостатньо коштів - не додаємо транзакцію
    else:
        wallet.deposit(amount)

    # Зберігаємо транзакцію і оновлений гаманець в data
    data["transactions"].append(transaction.to_dict())
    data["wallet"] = wallet.to_dict()
    update_tags(data, tags)

    # Зберігаємо в файл
    save_data(data, filename)
    print(f"\n✓ Транзакцію додано! Баланс: {wallet.balance} грн")


# ============================================================
# ПЕРЕГЛЯД ТРАНЗАКЦІЙ
# ============================================================

def filter_by_period(transactions, period):
    # Фільтрує транзакції за обраним періодом
    today = datetime.now()
    result = []

    for t in transactions:
        # Перетворюємо рядок дати в об'єкт datetime для порівняння
        t_date = datetime.strptime(t["date"], "%d.%m.%Y")

        if period == "week":
            # Останні 7 днів
            diff = (today - t_date).days
            if 0 <= diff <= 7:
                result.append(t)
        elif period == "month":
            # Поточний місяць і рік
            if t_date.month == today.month and t_date.year == today.year:
                result.append(t)
        elif period == "year":
            # Поточний рік
            if t_date.year == today.year:
                result.append(t)

    return result


def display_transactions(data, config):
    # Показує список транзакцій за обраний період згрупованих по днях
    print("\n" + "="*40)
    print("Перегляд транзакцій")
    print("="*40)

    period = choose_from_list(
        ["тиждень", "місяць", "рік"],
        "Оберіть період:"
    )
    period_map = {"тиждень": "week", "місяць": "month", "рік": "year"}
    transactions = filter_by_period(data["transactions"], period_map[period])

    if not transactions:
        print("Транзакцій за цей період немає")
        return

    # Групуємо транзакції по днях
    # Словник де ключ = дата, значення = список транзакцій
    by_day = {}
    for t in transactions:
        date = t["date"]
        if date not in by_day:
            by_day[date] = []
        by_day[date].append(t)

    # Виводимо по кожному дню
    page_size = config.get("page_size", 10)
    count = 0

    for date in sorted(by_day.keys(), reverse=True):
        day_transactions = by_day[date]
        day_total = sum(
            t["amount"] if t["trans_type"] == "income" else -t["amount"]
            for t in day_transactions
        )

        print(f"\n{date} | Підсумок дня: {day_total:+.2f} грн")
        print("-" * 40)

        for t in day_transactions:
            trans = Transaction.from_dict(t)
            trans.display()
            count += 1

            # Пагінація — зупиняємось після page_size записів
            if count % page_size == 0:
                more = input("\nПоказати більше? (Enter = так, n = ні): ").strip().lower()
                if more == "n":
                    return


# ============================================================
# РЕДАГУВАННЯ І ВИДАЛЕННЯ
# ============================================================

def find_transaction_by_id(data, trans_id):
    # Шукає транзакцію за ID і повертає її індекс в списку
    for i, t in enumerate(data["transactions"]):
        if t["id"] == trans_id:
            return i
    return None  # якщо не знайшла


def delete_transaction(data, filename):
    # Видаляє транзакцію за ID
    print("\n" + "="*40)
    print("Видалення транзакції")
    print("="*40)

    try:
        trans_id = int(input("Введіть ID транзакції для видалення: ").strip())
    except ValueError:
        print("Невірний ID")
        return

    index = find_transaction_by_id(data, trans_id)
    if index is None:
        print(f"Транзакцію з ID {trans_id} не знайдено")
        return

    t = data["transactions"][index]
    trans = Transaction.from_dict(t)
    trans.display()

    confirm = input("Видалити цю транзакцію? (y/n): ").strip().lower()
    if confirm != "y":
        print("Скасовано")
        return

    # Відновлюємо баланс гаманця
    wallet = Wallet.from_dict(data["wallet"])
    if t["trans_type"] == "expense":
        wallet.deposit(t["amount"])   # повертаємо гроші
    else:
        wallet.withdraw(t["amount"])  # знімаємо гроші

    # Видаляємо транзакцію зі списку
    data["transactions"].pop(index)
    data["wallet"] = wallet.to_dict()
    save_data(data, filename)
    print("✓ Транзакцію видалено")


def edit_transaction(data, filename):
    # Редагує існуючу транзакцію
    print("\n" + "="*40)
    print("Редагування транзакції")
    print("="*40)

    try:
        trans_id = int(input("Введіть ID транзакції для редагування: ").strip())
    except ValueError:
        print("Невірний ID")
        return

    index = find_transaction_by_id(data, trans_id)
    if index is None:
        print(f"Транзакцію з ID {trans_id} не знайдено")
        return

    t = data["transactions"][index]
    print("Поточна транзакція:")
    Transaction.from_dict(t).display()

    print("\nЩо редагувати? (Enter = залишити поточне значення)")

    # Редагування категорії
    categories = get_all_categories(data, t["trans_type"])
    print(f"Поточна категорія: {t['category']}")
    change_cat = input("Змінити категорію? (y/n): ").strip().lower()
    if change_cat == "y":
        t["category"] = choose_from_list(categories, "Нова категорія:")

    # Редагування суми
    print(f"Поточна сума: {t['amount']} грн")
    new_amount = input("Нова сума (або Enter): ").strip()
    if new_amount:
        try:
            old_amount = t["amount"]
            t["amount"] = float(new_amount)
            # Оновлюємо баланс з урахуванням різниці
            wallet = Wallet.from_dict(data["wallet"])
            diff = t["amount"] - old_amount
            if t["trans_type"] == "expense":
                wallet.balance -= diff
            else:
                wallet.balance += diff
            data["wallet"] = wallet.to_dict()
        except ValueError:
            print("Невірна сума, залишаю попередню")

    # Редагування дати
    print(f"Поточна дата: {t['date']}")
    new_date = input("Нова дата (ДД.ММ.РРРР або Enter): ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%d.%m.%Y")
            t["date"] = new_date
        except ValueError:
            print("Невірний формат дати, залишаю попередню")

    # Редагування тегів
    print(f"Поточні теги: {', '.join(t['tags'])}")
    change_tags = input("Змінити теги? (y/n): ").strip().lower()
    if change_tags == "y":
        t["tags"] = input_tags(data)
        update_tags(data, t["tags"])

    # Редагування коментаря
    print(f"Поточний коментар: {t['comment']}")
    new_comment = input("Новий коментар (або Enter): ").strip()
    if new_comment:
        t["comment"] = new_comment

    data["transactions"][index] = t
    save_data(data, filename)
    print("✓ Транзакцію оновлено")


# ============================================================
# ПОШУК ЗА ТЕГОМ
# ============================================================

def search_by_tag(data):
    # Шукає транзакції за одним тегом
    print("\n" + "="*40)
    print("Пошук за тегом")
    print("="*40)

    tags = get_all_tags(data)
    if not tags:
        print("В системі ще немає тегів")
        return

    tag = choose_from_list(tags, "Оберіть тег для пошуку:")

    # Шукаємо всі транзакції де є цей тег
    results = [t for t in data["transactions"] if tag in t.get("tags", [])]

    if not results:
        print(f"Транзакцій з тегом '{tag}' не знайдено")
        return

    print(f"\nЗнайдено {len(results)} транзакцій з тегом '{tag}':")
    for t in results:
        Transaction.from_dict(t).display()


# ============================================================
# УПРАВЛІННЯ КАТЕГОРІЯМИ
# ============================================================

def manage_categories(data, filename):
    # Меню управління категоріями
    while True:
        print("\n" + "="*40)
        print("Управління категоріями")
        print("="*40)
        action = choose_from_list(
            ["Переглянути всі", "Додати категорію", "Видалити категорію",
             "Редагувати категорію", "Назад"],
            "Оберіть дію:"
        )

        if action == "Переглянути всі":
            print("\nБазові категорії витрат:", ", ".join(DEFAULT_CATEGORIES["expense"]))
            print("Базові категорії доходів:", ", ".join(DEFAULT_CATEGORIES["income"]))
            print("Власні категорії витрат:", ", ".join(data["custom_categories"]["expense"]) or "немає")
            print("Власні категорії доходів:", ", ".join(data["custom_categories"]["income"]) or "немає")

        elif action == "Додати категорію":
            cat_type = choose_from_list(["expense", "income"], "Тип категорії:")
            name = input("Назва нової категорії: ").strip()
            if name:
                data["custom_categories"][cat_type].append(name)
                save_data(data, filename)
                print(f"✓ Категорію '{name}' додано")

        elif action == "Видалити категорію":
            cat_type = choose_from_list(["expense", "income"], "Тип категорії:")
            custom = data["custom_categories"][cat_type]
            if not custom:
                print("Немає власних категорій для видалення")
                continue
            cat = choose_from_list(custom, "Оберіть категорію для видалення:")
            data["custom_categories"][cat_type].remove(cat)
            save_data(data, filename)
            print(f"✓ Категорію '{cat}' видалено")

        elif action == "Редагувати категорію":
            cat_type = choose_from_list(["expense", "income"], "Тип категорії:")
            custom = data["custom_categories"][cat_type]
            if not custom:
                print("Немає власних категорій для редагування")
                continue
            cat = choose_from_list(custom, "Оберіть категорію для редагування:")
            new_name = input(f"Нова назва для '{cat}': ").strip()
            if new_name:
                idx = data["custom_categories"][cat_type].index(cat)
                data["custom_categories"][cat_type][idx] = new_name
                save_data(data, filename)
                print(f"✓ Категорію перейменовано на '{new_name}'")

        elif action == "Назад":
            break
