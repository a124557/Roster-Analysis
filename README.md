## Roster Analysis

This 'mlsplayers.py' script pulls all roster data for every team in the MLS using an API.
The API may not contain the most up-to-date information as this project was created for
learning purposes only free sources of information were used. The script will output 
all player data into a CSV file with several metrics pertaining to player performance
such as goals, assists, yellow/red cards, etcetera.

The 'rosterchange.py' script outputs a CSV file containing information about all
changes in roster data between two dates chosen by the user. This is done using the data saved by the 
'mlsplayers.py' script locally. 

'predict-popularity.py' is a script that using a machine learning linear regression model to
predict the 'Player Popularity' score based on features that are put into the model which are
goals, assists, and yellow/red cards.