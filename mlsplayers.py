import http.client
import json
import csv
import os.path

import requests
import time
from decouple import config
from datetime import datetime
from unidecode import unidecode
import difflib
from collections import defaultdict

api_key = config('API_KEY')
sportsDataIO_key = config('SPORTSDATA.IO_KEY')

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

""" Loading latest JSON file last generated from directory to check if it is from today.
If the file is from today, we don't need to call our APIs again. We just generate our 
outputs using the saved data"""

oldFile = False


def load_json_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            data = json.load(file)
        oldFile = True
        return data
    else:
        return None


# Define the file name format
file_name = f"{current_date} – MLS – APICALL.txt"

# Load the saved JSON data from the file
old_data_list = load_json_data(file_name)

if old_data_list is None:
    # Define the API endpoints
    player_info_endpoint = "https://api.sportsdata.io/v4/soccer/stats/json/PlayerSeasonStats/MLS/2023"

    # Make API requests and handle responses
    try:
        # Make the first API request
        response1 = requests.get(player_info_endpoint, params={"key": sportsDataIO_key})
        response1.raise_for_status()  # Raise an exception for HTTP errors

        # Process the responses
        player_info = response1.json()[0]['PlayerSeasons']

        # Do something with the data
        # print(player_info)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", str(e))

    # Create list to store general player data
    player_data = []

    # Create an empty dictionary to store player active dates and jersey numbers for entire league that we can quickly access later
    activeDate = {}

    """ Retrieving sportsdata.io data which contains information about player active date. This code is placed before the for
    loop because 1 call will retrieve data for the entire league. An individual call by team is not required"""
    # API call
    active_date_url = 'https://api.sportsdata.io/v4/soccer/scores/json/ActiveMemberships/MLS'

    # Making API call
    response5 = requests.get(active_date_url, params={"key": sportsDataIO_key})
    response5.raise_for_status()

    # Process the response
    player_activeDate = response5.json()

    for player in player_activeDate:
        name = player['PlayerName'].split()
        if len(name) >= 2:
            name = name[1]
        else:
            name = "N/A"
        activeDate[player['PlayerId']] = [datetime.fromisoformat(player['StartDate']).strftime('%Y-%m-%d'),
                                          player['Jersey']]

    # Traversing through list of players
    for player in player_info:
        # Splitting name into parts and only using the last name
        player_id = player.get('PlayerId', 'N/A')
        name_parts = player['Name'].split()
        if len(name_parts) > 1:
            name = name_parts[1].rstrip(' ')
        else:
            name = name_parts[0]
        team = player.get('Team', 'N/A')
        try:
            jersey_number = activeDate[player_id][1]
        except KeyError:
            # Set jersey_number to 'N/A' when the key is not found
            jersey_number = 'N/A'
        position = player.get('Position', 'N/A')
        offsides = player.get('Offsides', 'N/A')
        ownGoals = player.get('OwnGoals', 'N/A')
        tackles = player.get('Tackles', 'N/A')
        touches = player.get('Touches', 'N/A')
        games = player.get('Games', 'N/A')
        blockedShots = player.get('BlockedShots', 'N/A')
        goals_scored = player.get('Goals', 'N/A')
        assists = player.get('Assists', 'N/A')
        fouls = player.get('Fouls', 'N/A')
        minutes_played = player.get('Minutes', 'N/A')
        yellow_cards = player.get('YellowCards', 'N/A')
        red_cards = player.get('RedCards', 'N/A')
        tacklesWon = player.get('TacklesWon', 'N/A')
        shots_on_target = player.get('ShotsOnGoal', 'N/A')

        # Create a dictionary for the current player
        player = {
            'Team Name': team,
            'Last Name': name,
            'Jersey Number': jersey_number,
            'Position': position,
            'Offsides': offsides,
            'Own Goals': ownGoals,
            'Tackles': tackles,
            'Touches': touches,
            'Games Played': games,
            'Blocked Shots': blockedShots,
            'Goals': goals_scored,
            'Assists': assists,
            'Fouls': fouls,
            'Minutes Played': minutes_played,
            'Yellow Cards': yellow_cards,
            'Red Cards': red_cards,
            'Tackles Won': tacklesWon,
            'Shots on Target': shots_on_target,
            'Player ID': player_id,
            'Popularity Score': int(goals_scored + assists + (yellow_cards * -1) + (red_cards * -2))
        }

        # Appending active dates and proper last name with accents from other data source
        key = (player_id)
        if key in activeDate:
            player['Active Date'] = activeDate[key][0]
        else:
            player['Active Date'] = 'N/A'
            print("Active date info for " + name + "is not found.")

        # Keeping track and letter and jersey number counts
        letter_count = [0] * 26  # A-Z
        number_count = [0] * 10  # 0-9

        # Increment the letter count
        for letter in name:
            letter = letter.upper()
            if 'A' <= letter <= 'Z':
                letter_count[ord(letter) - ord('A')] += 1

        # Check if jersey_number is 'N/A' or None
        if jersey_number == 'N/A' or jersey_number is None:
            print("Jersey number is 'N/A' or None.")
        else:
            # Check if jersey_number is a valid number
            if str(jersey_number).isdigit():
                for number in str(jersey_number):
                    number_count[int(number)] += 1
            else:
                print("Jersey number is not a valid number.")

        # Append letter count to dictionary
        for index, count in enumerate(letter_count):
            letter = chr(index + ord('A'))
            if count == 0:
                count = ''
            player[f'{letter}'] = count

        # Append number count to dictionary
        for index, count in enumerate(number_count):
            # Using str(index) because chr(index) will produce some unprintable characters
            number = str(index)
            if count == 0:
                count = ''
            player[f'{number}'] = count

        player_data.append(player)

else:
    print("Found harvested API data that is from today. Using it to create the outputs.")
    player_data = old_data_list


# Comparing dictionaries with same 'Last Name' to check for differences in player data
def compare_last_names(old_data, new_data):
    if old_data is None:
        # Handle the case when old_data is None (e.g., file not found or empty)
        return []
    changes = defaultdict(lambda: {"Added": [], "Removed": []})

    for old_dict in old_data:
        player_id = old_dict.get('Player ID')
        for new_dict in new_data:
            if new_dict.get('Player ID') == player_id:
                # If we have found matching Last Names and Team Names, we compare the dictionaries
                d = difflib.Differ()
                old_items = sorted(old_dict.items())
                new_items = sorted(new_dict.items())
                diff = list(d.compare(old_items, new_items))

                # Check for differences, additions, and removals
                added = []
                removed = []
                for line in diff:
                    if line.startswith('+ '):
                        added.append(line[2:])
                    elif line.startswith('- '):
                        removed.append(line[2:])

                # Store changes for the 'Last Name' and 'Team Name' combination
                key = (player_id)
                changes[key]["Added"].extend(added)
                changes[key]["Removed"].extend(removed)
    return changes


# Writing current player data to text file in JSON format to compare later

# Compare the dictionaries with the same 'Last Name' and detect the changes
changes = compare_last_names(old_data_list, player_data)

if oldFile is True:
    # Write changes to a CSV file
    csv_file_name = f"{current_date} - MLS - Changes.csv"
    with open(csv_file_name, 'w', newline='') as csv_file:
        fieldnames = ['Last Name', 'Added', 'Removed']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for last_name, change in changes.items():
            if change["Added"] or change["Removed"]:
                writer.writerow({'Last Name': last_name, 'Added': ', '.join(change['Added']),
                                 'Removed': ', '.join(change['Removed'])})

# Open a file for writing the latest data
with open(file_name, "w") as file:
    # Convert the dictionary to a JSON string and write it to the file
    json.dump(player_data, file)

# Creating CSV for export
title = ['MLS - Toronto FC']

with open('roster_data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=player_data[0].keys())

    # Write the header
    writer.writeheader()

    # Writing data to different headers
    for player in player_data:
        writer.writerow(player)

print("CSV writing complete.")

# https://api.sportradar.us/soccer-extended/trial/v4/en/players/sr:player:48978/profile.json
