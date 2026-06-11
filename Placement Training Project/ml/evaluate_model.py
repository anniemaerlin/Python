import joblib
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# Load data
X_train, X_test, y_train, y_test = joblib.load(
    "ml/processed_data.pkl"
)

# Load models
rf = joblib.load(
    "ml/saved_models/random_forest_model.pkl"
)

xgb = joblib.load(
    "ml/saved_models/xgboost_model.pkl"
)

# Predictions
rf_pred = rf.predict(X_test)
xgb_pred = xgb.predict(X_test)

print("\nRandom Forest")
print("MAE:", mean_absolute_error(y_test, rf_pred))
print("RMSE:", mean_squared_error(y_test, rf_pred) ** 0.5)
print("R2:", r2_score(y_test, rf_pred))

print("\nXGBoost")
print("MAE:", mean_absolute_error(y_test, xgb_pred))
print("RMSE:", mean_squared_error(y_test, xgb_pred) ** 0.5)
print("R2:", r2_score(y_test, xgb_pred))