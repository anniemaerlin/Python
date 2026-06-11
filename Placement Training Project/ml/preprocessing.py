import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("dataset/dynamic_pricing_dataset_1000.csv")

# Drop unnecessary columns
df = df.drop(["Date", "Product_ID"], axis=1)

# Encode categorical columns
label_encoders = {}

categorical_cols = [
    "Day_of_Week",
    "Product",
    "Customer_Segment",
    "Promotion"
]

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Save encoders
joblib.dump(label_encoders, "label_encoders.pkl")

# Features and target
X = df.drop("Optimal_Price", axis=1)
y = df["Optimal_Price"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Save processed data
joblib.dump((X_train, X_test, y_train, y_test), "processed_data.pkl")

print("Preprocessing completed!")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))