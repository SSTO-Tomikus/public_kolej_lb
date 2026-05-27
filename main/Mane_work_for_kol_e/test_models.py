# test_models.py — pytest тести для курсової
# Запуск: pytest test_models.py -v

import pytest
import json
import os
from models import Transaction, Wallet, Category
from storage import save_data, load_data, get_all_categories, update_tags


# ============================================================
# ТЕСТИ ДЛЯ WALLET
# ============================================================

def test_wallet_creation():
    # Перевіряємо що гаманець створюється правильно
    wallet = Wallet("Основний", 1000)
    assert wallet.name == "Основний"
    assert wallet.balance == 1000


def test_wallet_default_balance():
    # Перевіряємо що початковий баланс = 0 якщо не вказано
    wallet = Wallet("Тест")
    assert wallet.balance == 0


def test_wallet_deposit():
    # Перевіряємо поповнення гаманця
    wallet = Wallet("Тест", 500)
    wallet.deposit(300)
    assert wallet.balance == 800


def test_wallet_withdraw_success():
    # Перевіряємо успішне списання
    wallet = Wallet("Тест", 1000)
    result = wallet.withdraw(300)
    assert result == True
    assert wallet.balance == 700


def test_wallet_withdraw_insufficient():
    # Перевіряємо що не можна списати більше ніж є
    wallet = Wallet("Тест", 100)
    result = wallet.withdraw(500)
    assert result == False
    assert wallet.balance == 100  # баланс не змінився


def test_wallet_to_dict():
    # Перевіряємо перетворення в словник
    wallet = Wallet("Основний", 1500)
    d = wallet.to_dict()
    assert d == {"name": "Основний", "balance": 1500}


def test_wallet_from_dict():
    # Перевіряємо створення з словника
    d = {"name": "Основний", "balance": 2000}
    wallet = Wallet.from_dict(d)
    assert wallet.name == "Основний"
    assert wallet.balance == 2000


# ============================================================
# ТЕСТИ ДЛЯ TRANSACTION
# ============================================================

def test_transaction_creation():
    # Перевіряємо створення транзакції
    t = Transaction(1, "expense", 150, "продукти", "2024-01-25", ["атб"])
    assert t.id == 1
    assert t.trans_type == "expense"
    assert t.amount == 150
    assert t.category == "продукти"
    assert t.date == "2024-01-25"
    assert t.tags == ["атб"]


def test_transaction_default_tags():
    # Перевіряємо що теги за замовчуванням порожні
    t = Transaction(1, "income", 5000, "зарплата", "2024-01-25")
    assert t.tags == []


def test_transaction_to_dict():
    # Перевіряємо перетворення в словник
    t = Transaction(1, "expense", 100, "транспорт", "2024-01-25", ["маршрутка"])
    d = t.to_dict()
    assert d["id"] == 1
    assert d["trans_type"] == "expense"
    assert d["amount"] == 100
    assert d["tags"] == ["маршрутка"]


def test_transaction_from_dict():
    # Перевіряємо створення з словника
    d = {
        "id": 2,
        "trans_type": "income",
        "amount": 5000,
        "category": "зарплата",
        "date": "2024-01-01",
        "tags": [],
        "comment": ""
    }
    t = Transaction.from_dict(d)
    assert t.id == 2
    assert t.amount == 5000


def test_transaction_roundtrip():
    # Перевіряємо що to_dict → from_dict зберігає всі дані
    original = Transaction(5, "expense", 250.5, "розваги", "2024-02-15", ["кіно"], "з другом")
    restored = Transaction.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.amount == original.amount
    assert restored.tags == original.tags
    assert restored.comment == original.comment


# ============================================================
# ТЕСТИ ДЛЯ CATEGORY
# ============================================================

def test_category_creation():
    cat = Category("продукти", "expense")
    assert cat.name == "продукти"
    assert cat.cat_type == "expense"


# ============================================================
# ТЕСТИ ДЛЯ STORAGE
# ============================================================

TEST_FILE = "test_data_temp.json"


def test_save_and_load_data():
    # Перевіряємо збереження і завантаження даних
    test_data = {
        "wallet": {"name": "Тест", "balance": 500},
        "transactions": [],
        "categories": {"expense": ["продукти"], "income": ["зарплата"]},
        "custom_categories": {"expense": [], "income": []},
        "tags": []
    }
    save_data(test_data, TEST_FILE)
    loaded = load_data(TEST_FILE)
    assert loaded["wallet"]["balance"] == 500
    assert loaded["wallet"]["name"] == "Тест"
    # Прибираємо тестовий файл після тесту
    os.remove(TEST_FILE)


def test_load_data_creates_default():
    # Перевіряємо що load_data повертає дефолтні дані якщо файл відсутній
    data = load_data("nonexistent_file_12345.json")
    assert "wallet" in data
    assert "transactions" in data
    assert data["transactions"] == []


def test_get_all_categories():
    # Перевіряємо що get_all_categories повертає базові + власні категорії
    data = load_data("nonexistent_file_12345.json")
    data["custom_categories"]["expense"].append("тест категорія")
    categories = get_all_categories(data, "expense")
    assert "продукти" in categories        # базова
    assert "тест категорія" in categories  # власна


def test_update_tags():
    # Перевіряємо що нові теги додаються без дублікатів
    data = {"tags": ["атб"]}
    update_tags(data, ["атб", "сільпо"])  # "атб" вже є
    assert "сільпо" in data["tags"]
    assert data["tags"].count("атб") == 1  # дублікатів немає
