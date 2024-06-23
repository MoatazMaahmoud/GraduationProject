import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB  # Import Gaussian Naive Bayes
from sklearn.ensemble import StackingClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import pickle
# Load your dataset (assuming it's a CSV file)
data = pd.read_csv("multi_processed_cleveland.csv")

# Check for non-numeric values and convert them
for column in data.columns:
    data[column] = pd.to_numeric(data[column], errors='coerce')
# Separate features (X) and target variable (y)
X = data.drop('num', axis=1)  
y = data['num']

# Normalize features
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Assign instance weights based on feature importance
feature_importances = np.array([0.1, 0.2, 0.05, 0.15, 0.1, 0.08, 0.12, 0.09, 0.1, 0.12, 0.1, 0.07, 0.02])

# Initialize base models
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=50)
naive_bayes_classifier = GaussianNB()  # Change this line to use Gaussian Naive Bayes

# Initialize the Stacking Classifier with Random Forest and Naive Bayes model
stacking_classifier = StackingClassifier(
    estimators=[('rf', rf_classifier), ('naive_bayes', naive_bayes_classifier)],  # Change 'linear' to 'naive_bayes'
    final_estimator=LogisticRegression(),
    cv=5,
    stack_method='predict_proba'  # Specify stack_method here
)

# Define parameter grid for grid search or distributions for random search
#param_grid = {
#    'final_estimator__C': [0.1, 1, 10],  # Regularization parameter for Logistic Regression
#    'rf__n_estimators': [50, 100, 200],  # Number of trees for Random Forest
#    'rf__max_depth': [None, 10, 20],      # Max depth for Random Forest (None means unlimited)
#}

# Alternatively, you can define distributions for random search
param_dist = {
    'final_estimator__C': [0.1, 1, 10],
    'rf__n_estimators': [50, 100, 200],
    'rf__max_depth': [None, 10, 20],
}

# Initialize GridSearchCV or RandomizedSearchCV
# grid_search = GridSearchCV(stacking_classifier, param_grid, cv=5, scoring='accuracy')
random_search = RandomizedSearchCV(stacking_classifier, param_distributions=param_dist, n_iter=10, cv=5, scoring='accuracy', random_state=42)

# Perform grid search or random search
# grid_search.fit(X_normalized, y)
random_search.fit(X_normalized, y)

# Print best parameters and best score
# print("Best parameters:", grid_search.best_params_)
# print("Best score:", grid_search.best_score_)
print("Best parameters:", random_search.best_params_)
print("Best score:", random_search.best_score_)

# Perform Cross-Validation with instance weights
kf = KFold(n_splits=7, shuffle=True, random_state=42)

# Define a function to compute instance weights for each fold
def compute_instance_weights(X_train):
    return X_train.dot(feature_importances)

# Perform cross-validation and get scores
cv_scores = cross_val_score(random_search.best_estimator_, X_normalized, y, cv=kf, scoring='accuracy')

# Print cross-validation scores
print("Cross-validation scores:", cv_scores)
print("Mean cross-validation score:", np.mean(cv_scores))

pickle.dump(random_search,open('multiclass_model.pkl','wb'))
model=pickle.load(open('multiclass_model.pkl','rb'))
# # Make predictions
# y_pred = rf_classifier.predict(X_test)
