# charts.py — кругова діаграма витрат (варіант 3, matplotlib)

from datetime import datetime

def get_transactions_for_period(transactions, period):
    # Фільтрує транзакції тільки витрати за обраний період
    today = datetime.now()
    result = []

    for t in transactions:
        if t["trans_type"] != "expense":
            continue  # показуємо тільки витрати на діаграмі
        t_date = datetime.strptime(t["date"], "%d.%m.%Y")

        if period == "week":
            if 0 <= (today - t_date).days <= 7:
                result.append(t)
        elif period == "month":
            if t_date.month == today.month and t_date.year == today.year:
                result.append(t)
        elif period == "year":
            if t_date.year == today.year:
                result.append(t)
        elif period == "all":
            result.append(t)

    return result


def show_pie_chart(data):
    # Показує кругову діаграму витрат згрупованих за категоріями
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Бібліотека matplotlib не встановлена.")
        print("Встановіть її командою: pip install matplotlib")
        return
pip install matplotlib
    from commands import choose_from_list

    period = choose_from_list(
        ["тиждень", "місяць", "рік", "весь час"],
        "Оберіть період для діаграми:"
    )
    period_map = {"тиждень": "week", "місяць": "month", "рік": "year", "весь час": "all"}

    transactions = get_transactions_for_period(
        data["transactions"],
        period_map[period]
    )

    if not transactions:
        print("Немає даних для відображення за цей період")
        return

    # Групуємо суми по категоріях
    # Словник: {"продукти": 500, "транспорт": 200, ...}
    category_totals = {}
    for t in transactions:
        cat = t["category"]
        if cat not in category_totals:
            category_totals[cat] = 0
        category_totals[cat] += t["amount"]

    # Готуємо дані для matplotlib
    labels = list(category_totals.keys())    # назви категорій
    sizes = list(category_totals.values())   # суми

    # Будуємо кругову діаграму
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",   # показує відсотки на кожному секторі
        startangle=90         # починаємо з верхньої точки
    )
    ax.set_title(f"Витрати за {period} по категоріях")
    plt.tight_layout()
    plt.show()
    print("✓ Діаграму відображено")
