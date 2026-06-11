import joblib
from xgboost import XGBRegressor

# Load processed data
X_train, X_test, y_train, y_test = joblib.load(
    "processed_data.pkl"
)

# Model
xgb = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    random_state=42
)

xgb.fit(X_train, y_train)

# Save model
joblib.dump(
    xgb,
    "ml/saved_models/xgboost_model.pkl"
)

print("XGBoost Model Saved!")