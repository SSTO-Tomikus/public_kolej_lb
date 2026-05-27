# models.py — опис основних об'єктів програми

class Category:
    # Категорія транзакції (наприклад "продукти" або "зарплата")
    def __init__(self, name, cat_type):
        self.name = name
        self.cat_type = cat_type  # "expense" = витрата, "income" = дохід


class Transaction:
    # Одна транзакція — витрата або дохід
    def __init__(self, id, trans_type, amount, category, date, tags=None, comment=""):
        self.id = id
        self.trans_type = trans_type  # "expense" або "income"
        self.amount = amount          # сума (число)
        self.category = category      # назва категорії
        self.date = date              # рядок "2024-01-25"
        self.tags = tags if tags is not None else []  # список тегів
        self.comment = comment        # короткий коментар

    def display(self):
        # Виводить транзакцію у зручному вигляді
        tags_str = ", ".join(self.tags) if self.tags else "немає"
        trans_type_ua = "Витрата" if self.trans_type == "expense" else "Дохід"
        print(f"[{self.id}] {trans_type_ua} | {self.category} | {self.amount} грн | {self.date} | теги: {tags_str}")

    def to_dict(self):
        # Перетворює об'єкт в словник для збереження в JSON
        return {
            "id": self.id,
            "trans_type": self.trans_type,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "tags": self.tags,
            "comment": self.comment
        }

    @staticmethod
    def from_dict(data):
        # Створює об'єкт Transaction зі словника (при завантаженні з JSON)
        return Transaction(
            id=data["id"],
            trans_type=data["trans_type"],
            amount=data["amount"],
            category=data["category"],
            date=data["date"],
            tags=data.get("tags", []),
            comment=data.get("comment", "")
        )


class Wallet:
    # Гаманець — має назву і баланс
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        # Поповнення балансу
        self.balance += amount

    def withdraw(self, amount):
        # Списання з балансу
        if amount > self.balance:
            print("Недостатньо коштів")
            return False  # повертає False якщо не вдалось списати
        self.balance -= amount
        return True  # повертає True якщо все добре

    def to_dict(self):
        # Перетворює гаманець в словник для збереження
        return {"name": self.name, "balance": self.balance}

    @staticmethod
    def from_dict(data):
        # Створює об'єкт Wallet зі словника
        return Wallet(name=data["name"], balance=data["balance"])
