import csv
import random
from datetime import datetime, timedelta

# Generate a random date range from 2021 to April 2025
start_date = datetime(2021, 1, 1)
end_date = datetime(2025, 4, 5)
delta = timedelta(days=1)

# Initial balance
monthly_income_2022_2023 = 8333  # Monthly income for 2022-2023
monthly_income_2024 = monthly_income_2022_2023  # Same income until promotion
daily_income_2022_2023 = round(monthly_income_2022_2023 / 30, 2)
daily_income_2024 = round(monthly_income_2024 / 30, 2)
daily_income_2024_post_promotion = round(monthly_income_2024 * 1.15 / 30, 2)  # 15% raise in late 2024

# Categories and their expense ranges
categories = {
    "Rent + Utilities": (1020, 1040),
    "Food": (10, 20),
    "Gas": (40, 60),
    "Groceries": (20, 100),
    "Health": (100, 590),
    "Subscriptions": (14, 30),
    "Travel": (50, 300),
    "Miscellaneous": (10, 50),
}

# Payment modes
payment_modes = ["Cash", "Credit Card", "Google Pay", "Amazon Pay"]

# Description examples
descriptions = {
    "Rent + Utilities": ["Monthly rent", "Utilities payment"],
    "Food": ["Takeout lunch", "Breakfast at diner", "Dinner from restaurant"],
    "Gas": ["Gas refill for car"],
    "Groceries": ["Weekly grocery shopping", "Restocking pantry items"],
    "Health": ["Doctor appointment", "Hospital bill"],
    "Subscriptions": ["Netflix subscription", "Amazon Prime", "Spotify Premium"],
    "Travel": ["Vacation flight tickets", "Hotel booking"],
    "Miscellaneous": ["Gift for friend", "Bought a book"],
}

# Generate data
data = []
current_date = start_date
balance = 5000  # Starting balance for the user

while current_date <= end_date:
    daily_expense = 0
    entries = []

    # Adjust daily income based on promotion
    if current_date.year == 2024 and current_date.month >= 10:
        daily_income = daily_income_2024_post_promotion
    elif current_date.year == 2024:
        daily_income = daily_income_2024
    else:
        daily_income = daily_income_2022_2023

    # Simulate paydays (1st of every month)
    if current_date.day == 1:
        balance += daily_income * 30  # Add monthly income

    # Good investments in late 2021
    if current_date.year == 2021 and current_date.month in [11, 12]:
        investment_return = random.randint(500, 1500)
        balance += investment_return
        entries.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Income": investment_return,
            "Expense": 0,
            "Category": "Investment Return",
            "Mode of Payment": "N/A",
            "Description": "Return from good investments",
            "Balance": round(balance, 2)
        })

    # Poor investments in late 2022
    if current_date.year == 2022 and current_date.month in [11, 12]:
        investment_loss = random.randint(500, 1500)
        balance -= investment_loss
        entries.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Income": 0,
            "Expense": investment_loss,
            "Category": "Investment Loss",
            "Mode of Payment": "N/A",
            "Description": "Loss from poor investments",
            "Balance": round(balance, 2)
        })

    # Simulate accident in mid-2023
    if current_date.year == 2023 and current_date.month == 6:
        accident_expense = 1000  # Fixed hospital bill
        daily_expense += accident_expense
        entries.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Income": 0,
            "Expense": accident_expense,
            "Category": "Health",
            "Mode of Payment": "Credit Card",
            "Description": "Hospital bill from accident",
            "Balance": round(balance - daily_expense, 2)
        })

    # Gifts in 2023 and 2024
    if current_date.year in [2023, 2024] and random.random() > 0.98:  # ~2% chance per day
        gift = random.randint(50, 500)
        balance += gift
        entries.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Income": gift,
            "Expense": 0,
            "Category": "Monetary Gift",
            "Mode of Payment": "N/A",
            "Description": "Received a gift",
            "Balance": round(balance, 2)
        })

    # Add daily expenses
    for category, (low, high) in categories.items():
        if random.random() > 0.6:  # Randomize daily expenses
            expense = round(random.uniform(low, high), 2)
            daily_expense += expense
            entries.append({
                "Date": current_date.strftime("%Y-%m-%d"),
                "Income": daily_income,
                "Expense": expense,
                "Category": category,
                "Mode of Payment": random.choice(payment_modes),
                "Description": random.choice(descriptions[category]),
                "Balance": round(balance - expense, 2)
            })

    # Update balance
    balance = balance - daily_expense + daily_income
    data.extend(entries)
    current_date += delta

# Write to CSV
with open("data.csv", mode="w", newline="", encoding='ISO-8859-1') as file:
    writer = csv.DictWriter(file, fieldnames=["Date", "Income", "Expense", "Category", "Mode of Payment", "Description", "Balance"])
    writer.writeheader()
    writer.writerows(data)

print("Refined dataset created! Check 'realistic_finances_with_subtle_variations.csv'.")