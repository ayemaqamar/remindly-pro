# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# ======= Sample Training Data =======
data = {
    "Urgency_Level": [1, 2, 3, 1, 3, 2, 1, 2, 3],
    "Days_Left": [5, 2, 0.5, 7, 0.2, 3, 4, 1.5, 0.1],
    "User_History_Delay": [0, 1, 1, 0, 1, 0, 0, 1, 1],
    "Priority_Label": ["Low", "Medium", "Urgent", "Low", "Urgent", "Medium", "Low", "Medium", "Urgent"]
}

df = pd.DataFrame(data)

# ======= Encode Labels =======
label_map = {"Low": 0, "Medium": 1, "Urgent": 2}
df["Priority_Label"] = df["Priority_Label"].map(label_map)

# ======= Train Model =======
X = df[["Urgency_Level", "Days_Left", "User_History_Delay"]]
y = df["Priority_Label"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# ======= Save Model =======
joblib.dump((model, label_map), "priority_model.pkl")

print("✅ Model trained and saved as priority_model.pkl")
