from flask import Flask, request, jsonify
import json
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import logging

app = Flask(__name__)

# Set up Flask logging
logging.basicConfig(level=logging.DEBUG)

# Load sales history data from the JSON file
def load_sales_data():
    try:
        with open("sales_history_dataset.json", "r") as json_file:
            sales_data = json.load(json_file)
        app.logger.debug("Loaded sales data successfully.")
        return sales_data
    except Exception as e:
        app.logger.error("Error loading sales data: %s", str(e))
        return {}

# Function to get sales data for a specific product, category, brand, and month
def get_sales_data(sales_data, product_name, category, brand, month):
    data = sales_data.get(month, [])
    app.logger.debug("Data for month %s: %s", month, data)

    # Filter data based on desired criteria
    filtered_data = [item for item in data if item["product"] == product_name and item["category"] == category and item["brand"] == brand]

    df = pd.DataFrame(filtered_data)
    return df

# ARIMA time series forecasting
def arima_forecast(data, order):
    print("Data for ARIMA analysis:", data) 
    model = ARIMA(data, order=order)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=1)
    return forecast[0]


def get_unique_brands(sales_data):
    unique_brands = set()
    for month_data in sales_data.values():
        for item in month_data:
            unique_brands.add(item["brand"])
    return unique_brands


# ABC analysis algorithm using ARIMA time series forecasting
def abc_analysis(sales_data, product_name, category, month, unique_brands, brand=None):
    current_year = datetime.now().year
    try:
        next_month = datetime.strptime(month, "%b").replace(year=current_year) + timedelta(days=31)
        app.logger.debug("Next month (datetime): %s", next_month)  # Add this line for debugging

        next_month_name = next_month.strftime("%b").lower()
        app.logger.debug("Next month name: %s", next_month_name) 

        app.logger.debug("Next month name: %s", next_month_name)  # Add this line for debugging

        if brand is not None:
            data = get_sales_data(sales_data, product_name, category, brand, next_month_name)
        else:
            data_list = [get_sales_data(sales_data, product_name, category, b, next_month_name) for b in unique_brands]
            app.logger.debug("Data list for all brands: %s", data_list)  # Add this line for debugging
            data = pd.concat(data_list)

        try:
            total_sales = data["sale"].sum()

            # Sort the data by sale value in descending order
            sorted_data = data.sort_values(by="sale", ascending=False)

            # Create a time series for sales data
            time_series_data = sorted_data["sale"].values
            app.logger.debug("Time series data for ARIMA analysis: %s", time_series_data)

            print("Data for ABC analysis:")  # Debug print
            print("Sales data for", brand, "brand:", data)  # Debug print
            print("Time series data:", time_series_data)  # Debug print
        except Exception as e:
            print("Error in abc_analysis function: %s", str(e))
            return None, None
        try:
            # Determine the best ARIMA order for the time series
            # You may need to adjust the p, d, and q values based on your data
            order = (3, 0, 1)

            # Use ARIMA forecast to predict stock quantity for the next time period (1 month in this case)
            predicted_stock_quantity = arima_forecast(time_series_data, order)

            # Determine the category based on the predicted stock quantity
            if predicted_stock_quantity >= total_sales * 0.6:
                category_prediction = "A"
            elif predicted_stock_quantity >= total_sales * 0.3:
                category_prediction = "B"
            else:
                category_prediction = "C"

            return predicted_stock_quantity, category_prediction

        except Exception as e:
            print("Error in ABC analysis for brand:", brand)
            print("Exception:", str(e))
            return None, None
        
    except Exception as e:
        print("Error in abc_analysis function: %s", str(e))
        return None, None   

@app.route("/predict_stock", methods=["POST"])
def predict_stock():
    try:
        data = request.get_json()
        product_name = data["product"]
        category = data["category"]
        month = data["month"].lower()
        app.logger.debug("Received data: %s", data) 
        sales_data = load_sales_data()
        unique_brands = get_unique_brands(sales_data)

        app.logger.debug("Received data: %s", data)
        app.logger.debug("Unique brands: %s", unique_brands)
        app.logger.debug("Keys available in sales_data dictionary: %s", sales_data.keys())  # Debug print

        prediction_results = []
        for brand in unique_brands:
            try:
                predicted_stock_quantity, category_prediction = abc_analysis(sales_data, product_name, category, month, unique_brands, brand=brand)
                result = {
                    "brand": brand,
                    "product": product_name,
                    "category": category,
                    "month": month,
                    "predictedStock": predicted_stock_quantity,
                    "predictedCategory": category_prediction
                }
                prediction_results.append(result)
            except Exception as e:
                app.logger.error("Error while processing brand: %s", brand)
                app.logger.error("Exception: %s", str(e))
                continue  # Skip this brand and continue with the next

        return jsonify(prediction_results), 200

    except Exception as e:
        app.logger.error("Error in predict_stock function: %s", str(e))
        return jsonify({"error": "An unexpected error occurred."}), 400



if __name__ == "__main__":
    app.run(debug=True)
