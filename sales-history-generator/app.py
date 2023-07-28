import random
import json
import calendar
import os
from datetime import datetime

# Function to generate random sales data
def generate_sales_data():
    products = ["shoes", "t-shirts", "jeans", "watches", "bags"]
    categories = ["male", "female", "unisex"]
    brands = ["adidas", "nike", "puma", "reebok", "vans"]
    unit_price_min, unit_price_max = 50.0, 500.0
    total_sold_min, total_sold_max = 50, 500

    data = {}
    for year in range(2012, 2022):  # Generate data for 10 years
        data[year] = {}
        for month in range(1, 13):  # Generate data for all 12 months
            month_name = calendar.month_abbr[month].lower()  # Get abbreviated month name (e.g., "jan", "feb", etc.)
            data[year][month_name] = []
            for _ in range(100):  # Generate 100 data points for each month
                product = random.choice(products)
                category = random.choice(categories)
                brand = random.choice(brands)
                unit_price = round(random.uniform(unit_price_min, unit_price_max), 2)
                total_sold = random.randint(total_sold_min, total_sold_max)
                unit_sold = random.randint(10, 100)  # Adding unitSold property
                sale = round(unit_price * unit_sold, 2)  # Adding sale property

                sale_data = {
                    "timestamp": f"{year}-{month_name}",  # Correct timestamp format
                    "product": product,
                    "category": category,
                    "brand": brand,
                    "unitPrice": unit_price,
                    "totalSold": total_sold,
                    "unitSold": unit_sold,  # Adding unitSold property
                    "sale": sale  # Adding sale property
                }

                data[year][month_name].append(sale_data)

    return data

# Generate sales data and save it to a JSON file
sales_data = generate_sales_data()

# Check if the JSON file exists and remove it
if os.path.exists("sales_history_dataset.json"):
    os.remove("sales_history_dataset.json")

with open("sales_history_dataset.json", "w") as json_file:
    json.dump(sales_data, json_file, indent=4)

print("Sales history dataset generated and saved to 'sales_history_dataset.json'.")
