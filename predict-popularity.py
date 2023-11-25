# This script will uses a simple linear regression model to predict player popularity
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load CSV file into DataFrame
df = pd.read_csv('roster_data.csv')

# Choose features and target variable
features = df[['Goals', 'Assists', 'Yellow Cards', 'Red Cards']]
# The target is what we want our model to predict
target = df['Popularity Score']

# Split the data into training and testing sets, X is a representation of the features and y the target
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Create the linear regression model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make prediction on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Square Error: {mse}')
print(f'R-squared: {r2}')

"""
1. Mean Squared Error (MSE)

Measures the average squared difference between the actual and predicted values. Larger errors are
penalized more heavily, making it sensitive to outliers. With linear regression, a lower MSE indicates 
a better fit of the model to the data


2. R-squared (R2) Score

R2 represents the proportion of the variance in the dependant variable that is predictable from the
independent variable. It ranges from 0 to 1, where 1 indicates a perfect fit. R2 provides an overall 
measure of how well the linear regression model explains variability in the data.

R-squared tells you how much of the variation in the outcome (dependent variable) your model can explain
using the predictors/features (independent variables). For example, a 0.8 R-squared value would suggest that 80%
of the variability in the outcome can be accounted for by your model. 
"""

# Visualize the prediction vs. actual values
# Scatter plot for y_test (blue)
plt.scatter(y_pred, y_test)

plt.xlabel('Actual Popularity Score')
plt.ylabel('Predicted Popularity Score')
plt.title('Actual vs. Predicted Popularity Score')
#plt.show()

# Make predictions for a new player
new_player_features = pd.DataFrame({
    'Goals': [3.8],
    'Assists': [2.5],
    'Yellow Cards': [7.6],
    'Red Cards': [0]
})

predicted_popularity = model.predict(new_player_features)
print(f'Predicted Popularity Score for the New Player: {predicted_popularity}')


