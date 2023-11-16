import json
import csv
import os
from datetime import datetime


# Load data from the latest and chosen date text files
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function extracting date from file names
def extract_date_from_file(filename):
    try:
        # Extract date part of filename
        date_str = filename.split(' - ')[0]
        # Converting the date string to datetime object
        return datetime.strptime(date_str, "%Y%,%d")
    except ValueError:
        # Handling case where filename doesn't follow expected format
        return None


# Load data from the latest and chosen date files
latest_data = load_data('20231115 – MLS – APICALL.txt')
chosen_date_data = load_data('20231029 – MLS – APICALL.txt')

# Identify common players based on 'Player ID'
common_players = [player for player in latest_data if
                  'Player ID' in player and player['Player ID'] in [p['Player ID'] for p in chosen_date_data]]

# Compare data and store changes (replace with your specific logic)
changes = []

# Detect missing players in the latest data
missing_players = [player for player in chosen_date_data if
                   'Player ID' in player and player['Player ID'] not in [p['Player ID'] for p in latest_data]]
for player in missing_players:
    change = {'Action': 'DELETE', 'Player ID': player['Player ID'], 'Last Name': player['Last Name'], 'Change':
        'Removed from league'}
    changes.append(change)

# Detect added players in the latest data
added_players = [player for player in latest_data if
                 'Player ID' in player and player['Player ID'] not in [p['Player ID'] for p in chosen_date_data]]
for player in added_players:
    change = {'Action': 'CREATE', 'Player ID': player['Player ID'], 'Last Name': player['Last Name'], 'Change':
        'Added to league'}
    changes.append(change)

for player in common_players:
    latest_player = next(p for p in latest_data if 'Player ID' in p and p['Player ID'] == player['Player ID'])
    chosen_date_player = next(p for p in chosen_date_data if 'Player ID' in p and p['Player ID'] == player['Player ID'])

    # Initialize a list to store changes for this player
    player_changes = []

    # Compare data and detect changes
    # For example, you can compare 'Last Name,' 'Team Name,' etc.
    """if latest_player.get('Last Name') != chosen_date_player.get('Last Name'):
        player_changes.append('Last Name: ' + chosen_date_player['Last Name'] + "-->" +
                              latest_player['Last Name'])
    if latest_player.get('Jersey Number') != chosen_date_player.get('Jersey Number'):
        player_changes.append('\nJersey Number: ' + str(chosen_date_player['Jersey Number']) + "-->" +
                              str(latest_player['Jersey Number']))"""
    # Repeat for other fields of interest
    for key, value in latest_player.items():
        try:
            if latest_player[key] != chosen_date_player[key]:
                player_changes.append(key + ": " + str(chosen_date_player[key]) + "--> " + str(latest_player[key]))
        except KeyError:
            print('A key was found that is not present in both files.')

    if len(player_changes) != 0:
        # Create a string with all changes for this player
        change_str = '\n'.join(player_changes)
        change = {'Action': 'UPDATE', 'Player ID': player['Player ID'], 'Last Name': player['Last Name'],
                  'Change': change_str}
        changes.append(change)

# Output changes to a CSV file
output_file = 'change_report.csv'
with open(output_file, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['Action', 'Player ID', 'Last Name', 'Change'])
    writer.writeheader()
    writer.writerows(changes)
