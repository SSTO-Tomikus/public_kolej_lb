# generator.py — генератор тестових даних
# Запуск: python generator.py --start_date 2024-01-01 --end_date 2024-03-01 --number_of_transactions 0-3

import json
import random
import argparse
from datetime import datetime, timedelta

# Категорії для генерації
DEFAULT_EXPENSE_CATEGORIES = ["продукти", "одяг", "транспорт", "розваги", "здоров'я", "навчання", "благодійність"]
DEFAULT_INCOME_CATEGORIES = ["стипендія", "заробітна плата", "інвестиційні надходження"]
DEFAULT_TAGS = ["атб", "сільпо", "розетка", "нова пошта", "аптека", "кафе", "спортзал"]


def generate_data(start_date, end_date, transactions_range, categories, tags, amount_range):
    # Генерує тестові транзакції за вказаний період

    result = []
    current_date = start_date
    trans_id = 1

    # Проходимо по кожному дню від start_date до end_date
    while current_date <= end_date:
        # Випадкова кількість транзакцій за день
        daily_count = random.randint(transactions_range[0], transactions_range[1])

        for _ in range(daily_count):
            # Випадковий тип транзакції
            trans_type = random.choice(["expense", "income"])

            # Вибираємо категорію
            if categories:
                category = random.choice(categories)
            elif trans_type == "expense":
                category = random.choice(DEFAULT_EXPENSE_CATEGORIES)
            else:
                category = random.choice(DEFAULT_INCOME_CATEGORIES)

            # Випадкова сума
            amount = round(random.uniform(amount_range[0], amount_range[1]), 2)

            # Випадковий тег (або без тегу)
            tag = [random.choice(tags)] if tags and random.random() > 0.3 else []

            result.append({
                "id": trans_id,
                "trans_type": trans_type,
                "amount": amount,
                "category": category,
                "date": current_date.strftime("%d.%m.%Y"),
                "tags": tag,
                "comment": ""
            })
            trans_id += 1

        # Переходимо до наступного дня
        current_date += timedelta(days=1)

    return result


def main():
    parser = argparse.ArgumentParser(description="Генератор тестових даних")
    parser.add_argument("--start_date", required=True, help="Початкова дата (РРРР-ММ-ДД)")
    parser.add_argument("--end_date", required=True, help="Кінцева дата (РРРР-ММ-ДД)")
    parser.add_argument("--number_of_transactions", default="1-3",
                        help="Кількість транзакцій на день (формат: М-N, наприклад 0-3)")
    parser.add_argument("--categories", nargs="*", help="Список категорій (необов'язково)")
    parser.add_argument("--tags", nargs="*", help="Список тегів (необов'язково)")
    parser.add_argument("--amount", default="10-1000",
                        help="Діапазон суми (формат: М-N, наприклад 10-1000)")
    parser.add_argument("--output", default="data.json", help="Файл для збереження даних")
    args = parser.parse_args()

    # Парсимо діапазони (розбиваємо рядок "0-3" на [0, 3])
    trans_range = list(map(int, args.number_of_transactions.split("-")))
    amount_range = list(map(float, args.amount.split("-")))

    start = datetime.strptime(args.start_date, "%d.%m.%Y")
    end = datetime.strptime(args.end_date, "%d.%m.%Y")

    transactions = generate_data(
        start_date=start,
        end_date=end,
        transactions_range=trans_range,
        categories=args.categories or [],
        tags=args.tags or DEFAULT_TAGS,
        amount_range=amount_range
    )

    # Зберігаємо в файл з повною структурою
    data = {
        "wallet": {"name": "Основний", "balance": 10000},
        "transactions": transactions,
        "categories": {
            "expense": DEFAULT_EXPENSE_CATEGORIES,
            "income": DEFAULT_INCOME_CATEGORIES
        },
        "custom_categories": {"expense": [], "income": []},
        "tags": DEFAULT_TAGS
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Згенеровано {len(transactions)} транзакцій → збережено в {args.output}")


if __name__ == "__main__":
    main()
