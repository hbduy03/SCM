import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from django.conf import settings


class DemandForecastAI:
    def __init__(self):
        self.model_dir = os.path.join(settings.MEDIA_ROOT, 'models')
        self.model_path = os.path.join(self.model_dir, 'forecasting_model.pkl')
        self.dataset_path = os.path.join(settings.MEDIA_ROOT, 'data', 'Historical Product Demand.csv')

        os.makedirs(self.model_dir, exist_ok=True)
        self.model = None
        self.unique_product_codes = []

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.unique_product_codes = data['codes']
                return True
            except:
                return False
        return False

    def train(self):
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path, usecols=['Date', 'Order_Demand', 'Product_Code', 'Warehouse'])

        df['Order_Demand'] = df['Order_Demand'].astype(str).str.replace('(', '', regex=False).str.replace(')', '',
                                                                                                          regex=False)
        df['Order_Demand'] = pd.to_numeric(df['Order_Demand'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna()

        df = df[df['Warehouse'] == 'Whse_C']

        product_counts = df['Product_Code'].value_counts()
        viable_products = product_counts[product_counts >= 10].index.tolist()

        df_train = df[df['Product_Code'].isin(viable_products)].copy()
        df_train = df_train.sort_values('Date')

        df_train['day_of_year'] = df_train['Date'].dt.dayofyear
        df_train['day_of_week'] = df_train['Date'].dt.dayofweek
        df_train['month'] = df_train['Date'].dt.month
        df_train['quarter'] = df_train['Date'].dt.quarter

        df_train['product_code_int'] = df_train['Product_Code'].astype('category').cat.codes

        X = df_train[['day_of_year', 'day_of_week', 'month', 'product_code_int']]
        y = df_train['Order_Demand']

        model = RandomForestRegressor(n_estimators=100, random_state=888, n_jobs=-1)
        model.fit(X, y)

        joblib.dump({'model': model, 'codes': viable_products}, self.model_path)
        self.model = model
        self.unique_product_codes = viable_products
        y_pred = model.predict(X)

        r2 = r2_score(y, y_pred)

        mae = mean_absolute_error(y, y_pred)


        print("\n===== MODEL PERFORMANCE =====")

        print(f"R² Score: {r2:.4f}")

        print(f"MAE: {mae:.4f}")

        print("================================\n")

        return {

            "r2": r2,

            "mae": mae,


        }

    def predict_product_demand(self, product_id_str):
        if not self.model or not self.unique_product_codes:
            return 0

        num_trained = len(self.unique_product_codes)
        mapped_idx = abs(hash(product_id_str)) % num_trained

        future_dates = pd.date_range(start=pd.Timestamp.now(), periods=30)
        future_df = pd.DataFrame({
            'day_of_year': future_dates.dayofyear,
            'day_of_week': future_dates.dayofweek,
            'month': future_dates.month,
            'product_code_int': mapped_idx
        })

        predictions = self.model.predict(future_df)
        raw_demand = int(np.sum(predictions))

        final_forecast = max(5, int(raw_demand / 100))

        return final_forecast

ai_engine = DemandForecastAI()