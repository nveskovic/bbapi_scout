import bb_api

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
bb_token = "BB token here"  # !!! NOT THE PASSWORD !!!

# 1. Login and get the seesion TODO: create an OOP aproach so that we can use bb_api as an object
s = bb_api.login(username, bb_token)

# 2. Do some actions
countries_and_leagues = bb_api.get_list_of_countries_and_league_levels(s)
leagues = []
for c_and_l in countries_and_leagues:
    cid = c_and_l["@id"]
    cdivisions = []
    if c_and_l["@divisions"] != "":
        clevels = int(c_and_l["@divisions"])
        cdivisions = range(1, clevels+1)
    leagues_to_append = bb_api.get_list_of_league_ids(s, country_id=cid, levels=cdivisions)
    for lid in leagues_to_append:
        leagues.append(lid)

# save list of leagues to file so that the script can run in chunks
teams_file = open("../all_leagues.txt", "w", encoding="UTF8")
teams_file.write(str(leagues))
teams_file.write("\n")
teams_file.close()

# leagues = bbapi_methods.get_list_of_league_ids(s, country_id=102, levels=[1,2])
teams = bb_api.get_list_of_non_bot_teams(s, league_ids=leagues)

# save list of teams to file so that the script can run in chunks
teams_file = open("../all_teams.txt", "w", encoding="UTF8")
teams_file.write(str(teams))
teams_file.write("\n")
teams_file.close()

players = bb_api.get_list_of_players(
    s, team_ids=teams,
    age_pattern="18|19|20",  # 18-20 years
    min_potential=4,
    country_id_pattern="29",  # 29 is ID for Serbia
    min_salary=0
)

# 3. Logout
url = "http://bbapi.buzzerbeater.com/logout.aspx"
s.get(url)

# Additional: do some more actions like writing to a file or similar
bb_api.save_players_to_tsv_files_by_country(players=players, file_name_prefix="players_by_country")
