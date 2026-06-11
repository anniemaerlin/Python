import joblib
from sklearn.ensemble import RandomForestRegressor

# Load processed data
X_train, X_test, y_train, y_test = joblib.load(
    "processed_data.pkl"
)

# Model
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

rf.fit(X_train, y_train)

# Save model
joblib.dump(
    rf,
    "ml/saved_models/random_forest_model.pkl"
)

print("Random Forest Model Saved!")