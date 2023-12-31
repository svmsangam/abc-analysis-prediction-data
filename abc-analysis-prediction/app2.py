import json
from flask import Flask, request, jsonify
import pandas as pd
import statsmodels.api as sm

app = Flask(__name__)

# Load sales history data from "sales_history_dataset.json"
with open("sales_history_dataset.json", "r") as json_file:
    sales_data = json.load(json_file)


# Implement the API endpoint for ABC analysis prediction using ARIMA time series
@app.route("/abc_analysis_prediction", methods=["POST"])
def abc_analysis_prediction():
    # Get parameters from the request payload
    data = request.get_json()
    product_name = data.get("productName")
    category = data.get("category")
    month = data.get("month")

    # Filter sales data based on product name, category, and month
    selected_data = []
    for year, months_data in sales_data.items():
        if month.lower() in months_data and category.lower() in ("all", category.lower()):
            for sale_data in months_data[month.lower()]:
                if (
                    sale_data["product"].lower() == product_name.lower()
                    and sale_data["category"].lower() == category.lower()
                ):
                    selected_data.append(sale_data)

    if not selected_data:
        return jsonify({"error": "No data found for the provided parameters."})

    # Prepare data for ARIMA time series forecasting
    df = pd.DataFrame(selected_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%b")
    df.set_index("timestamp", inplace=True)

    # Create an empty dictionary to store revenue for each brand
    brand_revenues = {}

    # Group data by brand and perform ARIMA forecasting for each brand
    for brand, brand_data in df.groupby("brand"):
        # Perform ARIMA forecasting (You will need to tune the model based on your data)
        # Example ARIMA model fitting:
        model = sm.tsa.ARIMA(brand_data["unitSold"], order=(1, 1, 1))
        results = model.fit()

        # Forecast the quantity required to be in stock for the brand
        forecast_steps = 1  # Forecast for one step (next month)
        forecast = results.forecast(steps=forecast_steps)

        # Calculate total revenue for the brand by multiplying forecasted quantity with the product price
        total_revenue = (brand_data["unitPrice"] * forecast.iloc[0]).sum()

        # Store the revenue in the dictionary with the brand as the key
        brand_revenues[brand] = total_revenue

    return jsonify(brand_revenues)


if __name__ == "__main__":
    app.run(debug=True)
