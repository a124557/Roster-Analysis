import http.client
import json
import csv
import requests
import time

api_key = "8g9twk5h7n5u4wzmfhckps69"

# Define the API endpoints
team_info_endpoint = "https://api.sportradar.us/soccer-extended/trial/v4/en/seasons/sr:season:101055/info.json"

# Player season stats by team (add goals, assists, chances created, minutes played, yellow cards, red cards
#https://api.sportradar.us/soccer-extended/trial/v4/en/seasons/sr:season:101055/competitors/sr:competitor:2513/statistics.json?api_key=7sw347q349he6cn5tjpt8cq8

# Make API requests and handle responses
try:
    # Make the first API request
    response1 = requests.get(team_info_endpoint, params={"api_key": api_key})
    response1.raise_for_status()  # Raise an exception for HTTP errors

    # Process the responses
    team_info_data = response1.json()

    # Do something with the data
    team_list = team_info_data['stages'][0]['groups'][0]['competitors']
    print("Team Data:", team_info_data['stages'][0]['groups'][0]['competitors'])
    #print("Competitor Profile Data:", competitor_profile_data)

except requests.exceptions.RequestException as e:
    print("An error occurred:", str(e))

team_data = []

for team in team_list:
    team_data.append(team['id'])


# Processing player data for entire league

# Create dictionary to store general player data
player_data = []
competitor_profile_data = ''
teamName = ""

for teamid in team_data:

    # Create a temp dictionary (hash map) to store extended seasonal player data that is then stored in the main dictionary
    seasonalData = {}

    try:
        # API call
        time.sleep(1)
        competitor_profile_endpoint = "https://api.sportradar.us/soccer-extended/trial/v4/en/competitors/" + teamid + "/profile.json"
        seasonal_player_data_endpoint = "https://api.sportradar.us/soccer-extended/trial/v4/en/seasons/sr:season:101055/competitors/" + teamid + "/statistics.json"

        # Make the second API request
        response2 = requests.get(competitor_profile_endpoint, params={"api_key": api_key})
        response2.raise_for_status()

        time.sleep(1)
        # Make third API request for seasonal player data
        response3 = requests.get(seasonal_player_data_endpoint, params={"api_key": api_key})
        response3.raise_for_status()

        # Process the responses
        competitor_profile_data = response2.json()
        seasonal_profile_player_data = response3.json()['competitor']['players']

        # We loop through seasonal player data and store each players data into the hashmap with their playerid as the key
        for seasonPlayerData in seasonal_profile_player_data:
            seasonalData[seasonPlayerData['id']] = seasonPlayerData

        # Check if the data is not empty
        if competitor_profile_data and 'competitor' in competitor_profile_data:
            team_name = competitor_profile_data['competitor']['name']
            teamName = team_name
            print("Team Name:", team_name)
        else:
            print(f"No data found for {teamid}")

        # Traversing through list of players
        for player in competitor_profile_data['players']:
            # Splitting name into parts and only using the last name
            name_parts = player['name'].split()
            name = name_parts[0].rstrip(', ')
            jersey_number = player.get('jersey_number', 'N/A')
            position = player.get('type', 'N/A')
            nationality = player.get('nationality', 'N/A')
            dob = player.get('date_of_birth', 'N/A')
            height = player.get('height', 'N/A')
            weight = player.get('weight', 'N/A')
            preferredFoot = player.get('preferred_foot', 'N/A')
            birthPlace = player.get('place_of_birth', 'N/A')

            # Retrieving extended seasonal player data from third endpoint such as goals, cards, assists, etc
            try:
                goals_scored = seasonalData[player['id']]['statistics']['goals_scored']
                assists = seasonalData[player['id']]['statistics']['assists']
                chances_created = seasonalData[player['id']]['statistics']['chances_created']
                minutes_played = seasonalData[player['id']]['statistics']['minutes_played']
                yellow_cards = seasonalData[player['id']]['statistics']['yellow_cards']
                red_cards = seasonalData[player['id']]['statistics']['red_cards']
                dribbles_completed = seasonalData[player['id']]['statistics']['dribbles_completed']
                shots_on_target = seasonalData[player['id']]['statistics']['shots_on_target']
            except KeyError:
                print(f"Player with ID '{player['id']} not found in seasonal data API endpoint")
                goals_scored = assists = chances_created = minutes_played = yellow_cards = red_cards = \
                    dribbles_completed = shots_on_target = 'N/A'

            # Create a dictionary for the current player
            player = {
                'Team Name': teamName,
                'Last Name': name,
                'Jersey Number': jersey_number,
                'Position': position,
                'Nationality': nationality,
                'DOB': dob,
                'Height (cm)': height,
                'Weight (kg)': weight,
                'Preferred Foot': preferredFoot,
                'Place of Birth': birthPlace,
                'Goals': goals_scored,
                'Assists': assists,
                'Chances Created': chances_created,
                'Minutes Played': minutes_played,
                'Yellow Cards': yellow_cards,
                'Red Cards': red_cards,
                'Dribbles Completed': dribbles_completed,
                'Shots on Target': shots_on_target,

            }

            # Keeping track and letter and jersey number counts
            letter_count = [0] * 26 # A-Z
            number_count = [0] * 10 # 0-9

            # Increment the letter count
            for letter in name:
                letter_count[ord(letter.upper()) - ord('A')] += 1

            # Increment number count. Checking first if it is 'N/A' before processing
            if jersey_number != 'N/A':
                for number in str(jersey_number):
                    number_count[int(number)] += 1

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

    except requests.exceptions.RequestException as e:
        print("An error occurred:", str(e))
        

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
