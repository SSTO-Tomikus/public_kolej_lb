# storage.py — збереження і завантаження даних з JSON файлу

import json
import os

# Базові категорії які не можна видалити або редагувати
DEFAULT_CATEGORIES = {
    "expense": ["продукти", "одяг", "транспорт", "розваги", "здоров'я", "навчання", "благодійність"],
    "income": ["стипендія", "заробітна плата", "інвестиційні надходження"]
}


def save_data(data, filename):
    # Зберігає всі дані програми в JSON файл
    # "w" = write, перезаписує файл кожного разу
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        # ensure_ascii=False — щоб українські літери зберігались нормально
        # indent=2 — щоб файл був читабельним з відступами


def load_data(filename):
    # Завантажує дані з JSON файлу
    # Якщо файл не існує — повертає початкову структуру
    if not os.path.exists(filename):
        return {
            "wallet": {"name": "Основний", "balance": 0},
            "transactions": [],
            "categories": DEFAULT_CATEGORIES,
            "custom_categories": {
                # власні категорії які можна редагувати і видаляти
                "expense": [],
                "income": []
            },
            "tags": []  # всі теги що коли-небудь використовувались
        }

    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_categories(data, cat_type):
    # Повертає список всіх категорій (базових + власних) для типу expense або income
    default = data["categories"].get(cat_type, [])
    custom = data["custom_categories"].get(cat_type, [])
    return default + custom


def get_all_tags(data):
    # Повертає всі теги що є в системі
    return data.get("tags", [])


def update_tags(data, new_tags):
    # Додає нові теги до загального списку (без дублікатів)
    existing = set(data.get("tags", []))
    for tag in new_tags:
        existing.add(tag)
    data["tags"] = list(existing)
