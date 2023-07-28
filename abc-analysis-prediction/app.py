from flask import Flask, request, jsonify
import json
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)

# Load sales history data from the JSON file
def load_sales_data():
    with open("sales_history_dataset.json", "r") as json_file:
        sales_data = json.load(json_file)

    # Convert the timestamp in the format "YYYY-Month" to "YYYY-Mon" (e.g., "2012-Jan")
    for year in sales_data:
        for month_name in list(sales_data[year].keys()):
            month_abbr = month_name[:3]  # Get the first 3 characters to create the abbreviated month name
            sales_data[year][month_abbr] = sales_data[year].pop(month_name)

    return sales_data


# Function to get sales data for a specific product, category, brand, and month
def get_sales_data(sales_data, product_name, category, brand, month_name):
    df = pd.DataFrame(sales_data)
    filtered_df = df[(df["product"] == product_name) & (df["category"] == category) & (df["brand"] == brand) & (df["month"] == month_name)]
    return filtered_df

# ARIMA time series forecasting
def arima_forecast(data, order):
    model = ARIMA(data, order=order)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=1)
    return forecast[0]

# ABC analysis algorithm using ARIMA time series forecasting
def abc_analysis(sales_data, product_name, category, brand, month_name):
    data = get_sales_data(sales_data, product_name, category, brand, month_name)
    total_sales_in_month = data["sale"].sum()

    # Sort the data by sale value in descending order
    sorted_data = data.sort_values(by="sale", ascending=False)

    # Create a time series for sales data
    time_series_data = sorted_data["sale"].values

    # Determine the best ARIMA order for the time series
    # You may need to adjust the p, d, and q values based on your data
    order = (3, 0, 1)

    # Use ARIMA forecast to predict stock quantity for the next time period (1 month in this case)
    predicted_stock_quantity = arima_forecast(time_series_data, order)

    # Determine the category based on the predicted stock quantity
    if predicted_stock_quantity >= total_sales_in_month * 0.6:
        category_prediction = "A"
    elif predicted_stock_quantity >= total_sales_in_month * 0.3:
        category_prediction = "B"
    else:
        category_prediction = "C"

    return predicted_stock_quantity, category_prediction

@app.route("/predict_stock", methods=["POST"])
def predict_stock():
    try:
        data = request.get_json()
        product_name = data["product"]
        category = data["category"]
        month_name = data["month"]

        sales_data = load_sales_data()
        unique_brands = {item["brand"] for year_data in sales_data.values() for month_data in year_data.values() for item in month_data}
        print("Received data:", data)
        print("Unique brands:", unique_brands)

        prediction_results = []
        for brand in unique_brands:
            predicted_stock_quantity, category_prediction = abc_analysis(sales_data, product_name, category, brand, month_name)
            result = {
                "brand": brand,
                "product": product_name,
                "category": category,
                "month": month_name,
                "predictedStock": predicted_stock_quantity,
                "predictedCategory": category_prediction
            }
            prediction_results.append(result)

        return jsonify(prediction_results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
