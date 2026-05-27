# config.py — завантаження налаштувань програми

import argparse
import json
import os

ENV_DATA_FILE = "FINANCE_DATA_FILE"
ENV_PAGE_SIZE = "FINANCE_PAGE_SIZE"


def load_config():
    # Базові значення — використовуються якщо нічого іншого не задано
    config = {
        "data_file": "data.json",
        "page_size": 10
    }

    # Крок 1: Змінні оточення (третій пріоритет)
    if os.environ.get(ENV_DATA_FILE):
        config["data_file"] = os.environ.get(ENV_DATA_FILE)
    if os.environ.get(ENV_PAGE_SIZE):
        config["page_size"] = int(os.environ.get(ENV_PAGE_SIZE))

    # Крок 2: Читаємо аргументи командного рядка
    parser = argparse.ArgumentParser(description="Система обліку фінансів")
    parser.add_argument("--config", help="шлях до файлу конфігурації")
    parser.add_argument("--data-file", help="шлях до файлу даних")
    parser.add_argument("--page-size", type=int, help="кількість записів на сторінці")
    args, _ = parser.parse_known_args()

    # Крок 3: Файл конфігурації (другий пріоритет)
    if args.config and os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            file_config = json.load(f)
            config.update(file_config)

    # Крок 4: Аргументи командного рядка (перший пріоритет)
    if args.data_file:
        config["data_file"] = args.data_file
    if args.page_size:
        config["page_size"] = args.page_size

    return config
