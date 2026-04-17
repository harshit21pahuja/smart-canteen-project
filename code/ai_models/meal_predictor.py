import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_tomorrow_meals(db_path="database.db"):
    # Simulated AI Model for Predicting future meals
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Fetch historical data
    cur.execute("SELECT breakfast_count, lunch_count, snacks_count, dinner_count FROM historical_meals ORDER BY date ASC")
    rows = cur.fetchall()
    conn.close()
    
    if len(rows) < 3:
        return {"breakfast": 0, "lunch": 0, "snacks": 0, "dinner": 0}
        
    # Prepare data for Simple Machine Learning (Linear Regression)
    X = np.arange(len(rows)).reshape(-1, 1) # temporal component
    predictions = {}
    
    labels = ["breakfast", "lunch", "snacks", "dinner"]
    for i, label in enumerate(labels):
        y = np.array([row[i] for row in rows])
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict for the next day
        pred_y = model.predict([[len(rows)]])
        predictions[label] = max(0, int(round(pred_y[0])))
        
    return predictions
