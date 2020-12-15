import bbapi_methods

#### READ ME ####
#
# This is the example driver script
# You can create your own scripts by using this one as an example.

# Steps needed:
# 1. Login
# 2. Do some actions
# 3. Logout

###### Main actions ######
username = "username here"
bb_token = "bbapi token (access token) here"

# 1. Login and get the seesion TODO: create an OOP aproach so that we can use bb_scout as an object
s = bbapi_methods.login(username, bb_token)

# 2. Do some actions
leagues = bbapi_methods.get_list_of_league_ids(s, country_id=29, levels=[1, 2, 3, 4])
teams = bbapi_methods.get_list_of_non_bot_teams(s, league_ids=leagues)

# to filter by nationality IDs, you need to use a regular expression
# example for Serbia (ID is 29):
# players = bbapi_methods.get_list_of_players(
#   s, team_ids=teams, age_pattern="18|19",
#   min_potential=6,
#   country_id_pattern="29",
#   min_salary=0
# )

# save list of teams to file so that the script can run in chunks
# teams_file = open("all_serbian_teams.txt", "w", encoding="UTF8")
# teams_file.write(str(teams))
# teams_file.write("\n")
# teams_file.close()q

players = bbapi_methods.get_list_of_players(
    s, team_ids=teams,
    age_pattern="18|19",
    min_potential=0,
    country_id_pattern="29",
    min_salary=0
)



# 3. Logout
url = "http://bbapi.buzzerbeater.com/logout.aspx"
s.get(url)

# Additional: do some more actions like writing to a file or similar
bbapi_methods.save_players_to_tsv_file(players=players, file_path="serbia_draft_51_lige_IV.tsv")
