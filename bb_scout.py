import sys
from random import randint

import requests
import xmltodict, json
from time import sleep
from bb_api_scout import bbapi_methods


###### Main actions ######
s = bbapi_methods.login()

leagues = bbapi_methods.get_list_of_league_ids(s, country_id=1, levels=[1, 2, 3, 4])
teams = bbapi_methods.get_list_of_non_bot_teams(s, league_ids=leagues)

# to filter by nationality IDs, you need to use a regular expression
# example for Serbia (ID is 29):
# players = bbapi_methods.get_list_of_players(
#   s, team_ids=teams, age_pattern="{18,19}",
#   min_potential=6,
#   country_id_pattern="29",
#   min_salary=0
# )

# save list of teams to file so that the script can run in chunks
teams_file = open("all_teams.txt", "w", encoding="UTF8")
teams_file.write(teams)
teams_file.write("\n")
teams_file.close()

players = bbapi_methods.get_list_of_players(
    s, team_ids=teams,
    age_pattern="[2-3][0-9]",
    min_potential=8,
    country_id_pattern=".*",
    min_salary=80000
)



# Logout
url = "http://bbapi.buzzerbeater.com/logout.aspx"
s.get(url)

for player in players:
    print(player)
print("Total number of players: {}".format(len(players)))

bbapi_methods.save_players_to_tsv_file(players=players, file_path="players2.tsv")
