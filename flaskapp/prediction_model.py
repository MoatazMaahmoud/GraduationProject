import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pickle
# Load your dataset (assuming it's a CSV file)
data = pd.read_csv("./cleaned_dataset.csv")

# Separate features (X) and target variable (y)
X = data.drop('target', axis=1)  
y = data['target']

# Normalize features
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Assign instance weights based on feature importance
# Example: You may compute feature importance and assign weights accordingly
feature_importances = np.array([0.23, 0.07, 0.16, 0.11, 0.21, 0.02, 0.05, 0.18, 0.02, 0.09, 0.14])

# Compute instance weights
instance_weights = X_normalized.dot(feature_importances)  # Compute dot product

# Initialize Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=49)

# Perform Cross-Validation with instance weights
cv_scores = cross_val_score(rf_classifier, X_normalized, y, cv=10, fit_params={'sample_weight': instance_weights})  # 10-fold cross-validation

print("Cross-validation scores:", cv_scores)
print("Mean cross-validation score:", np.mean(cv_scores))

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=49)

# Convert X_train to DataFrame to access its index
X_train_df = pd.DataFrame(X_train, columns=X.columns)
instance_weights_train = instance_weights[X_train_df.index]

# Train the model with instance weights
rf_classifier.fit(X_train, y_train, sample_weight=instance_weights_train)

pickle.dump(rf_classifier,open('model.pkl','wb'))
model=pickle.load(open('model.pkl','rb'))
# # Make predictions
# y_pred = rf_classifier.predict(X_test)
