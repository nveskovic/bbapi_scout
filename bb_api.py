import sys
from random import randint
from time import sleep

import requests
import xmltodict

base_url = "http://bbapi.buzzerbeater.com/"

###############################################################################
# Sleep settings
# !!!! DO NOT CHANGE THIS CONFIG as BB admins might close your account !!!
use_random_sleeps = True
min_sleep = 1  # seconds
max_sleep = 2  # seconds
###############################################################################


def login(username, bb_token):
    s = requests.Session()
    url = base_url + "login.aspx?login=" + username + "&code=" + bb_token
    payload = {}
    headers = {}
    response = s.get(url, headers=headers, data=payload)
    o = xmltodict.parse(response.text.encode('utf8'))
    try:
        result = o["bbapi"]["loggedIn"]  # if there is loggedIn all is ok
        return s
    except:
        sys.stderr.write("Not able to login to bbapi. {}\n".format(o))
        exit(1)


def teaminfo(s, teamid):
    url = base_url + "teaminfo.aspx?teamid={}".format(teamid)
    response = _get_(s, url)
    o = xmltodict.parse(response.text.encode('utf8'))
    return o["bbapi"]["team"]


def player(s, playerid):
    url = base_url + "player.aspx?playerid={}".format(playerid)
    response = _get_(s, url)
    o = xmltodict.parse(response.text.encode('utf8'))
    return o["bbapi"]["player"]


def get_list_of_countries_and_league_levels(s):
    countries = []
    url = base_url + "countries.aspx"
    response = _get_(s, url)
    o = xmltodict.parse(response.text.encode('utf8'))
    for country in o["bbapi"]["countries"]["country"]:
        countries.append(country)
        #print(country)
    return countries


def get_list_of_league_ids(s, country_id=29, levels=[1, 2, 3]):
    league_ids = [];
    total = len(levels)
    current = 0
    for level in levels:
        if use_random_sleeps:
            sec = randint(min_sleep, max_sleep)
            sleep(sec)

        current += 1
        progress_bar(
            "Getting league IDs: Country ID: {}, Division: {}".format(country_id, level),
            current, total)

        url = base_url + "leagues.aspx?countryid=" + str(
            country_id) + "&level=" + str(level)
        response = _get_(s, url)
        o = xmltodict.parse(response.text.encode('utf8'))
        num_of_leagues_found = len(o["bbapi"]["division"]["league"])
        if num_of_leagues_found <= 2:
            # single league is returned
            league_ids.append(o["bbapi"]["division"]["league"]['@id'])
        else:
            # we have multiple leagues found
            for league in o["bbapi"]["division"]["league"]:
                league_ids.append(league['@id'])
        # end for
    # end for

    # sys.stdout.write("For country ID:{} and divisions:{} found {} league(s).\n"
    #                  .format(country_id, str(levels), len(league_ids)))
    return league_ids


def get_list_of_non_bot_teams(s, league_ids=[]):
    return get_list_of_teams(
        s, league_ids,
        params={
            "include_bots": False,
            "include_active": True
        })


def get_list_of_teams_registered_from(s, league_ids, registered_from="1970-01-01"):
    date_registered_from = datetime.strptime(registered_from, '%Y-%m-%d')
    team_ids = get_list_of_non_bot_teams(s, league_ids=league_ids)
    teams_to_return = []

    total = len(team_ids)
    current = 0

    # filter the teams that are registered after the date
    for team_id in team_ids:
        try:
            if use_random_sleeps:
                sec = randint(min_sleep, max_sleep)
                # print("Sleeping {} seconds...".format(sec))
                sleep(sec)

            current += 1
            progress_bar(
                "Getting teams registered after {}. Checking team: {}".format(registered_from, team_id),
                current, total)

            url = base_url + "teaminfo.aspx?teamid=" + str(
                team_id)
            response = _get_(s, url)
            o = xmltodict.parse(response.text.encode('utf8'))

            create_date = o["bbapi"]["team"]["createDate"]
            team_registered_at = datetime.strptime(
                create_date,
                '%Y-%m-%dT%H:%M:%SZ')

            if date_registered_from <= team_registered_at:
                teams_to_return.append(team_id)
        except:
            sys.stderr.write("Not able to process teaminfo for team id:{}, {}\n".format(team_id, response.content))

    return teams_to_return


def get_list_of_teams(
        s, league_ids=[],
        params={
            "include_bots": False,
            "include_active": True
        }
):
    team_ids = []
    include_bots = params["include_bots"]
    include_active = params["include_active"]

    total = len(league_ids)
    current = 0

    for league_id in league_ids:
        try:
            if use_random_sleeps:
                sec = randint(min_sleep, max_sleep)
                # print("Sleeping {} seconds...".format(sec))
                sleep(sec)

            current += 1
            progress_bar(
                "Getting teams from leagues. Current league: {}".format(league_id),
                current, total)

            url = base_url + "standings.aspx?leagueid=" + str(
                league_id)
            response = _get_(s, url)
            o = xmltodict.parse(response.text.encode('utf8'))
            # loop through conferences
            for conference in o["bbapi"]["standings"]["regularSeason"][
                "conference"]:
                for team in conference["team"]:
                    if team['isBot'] == '0' and include_active:
                        team_ids.append(team['@id'])
                    elif team['isBot'] == '1' and include_bots:
                        team_ids.append(team['@id'])
        except:
            sys.stderr.write("Not able to process league id:{}, {}\n".format(league_id, response.content))

    return team_ids


def get_list_of_players(s, team_ids=[], age_pattern=".*", min_potential=6,
                        country_id_pattern=".*", min_salary=0):
    players = []
    total = len(team_ids)
    current = 0

    for team_id in team_ids:

        if use_random_sleeps:
            sec = randint(min_sleep, max_sleep)
            sleep(sec)

        url = base_url + "roster.aspx?teamid=" + str(
            team_id)
        response = _get_(s, url)
        o = xmltodict.parse(response.text.encode('utf8'))

        current += 1
        progress_bar(
            "Getting players from teams: Current team: {}".format(team_id),
            current, total)

        # some teams have only 1 player in the roster.
        # Check if that is the case and handle it specially
        roster = []
        try:
            if type(o["bbapi"]["roster"]["player"]) is collections.OrderedDict:
                # Single player rosters
                roster.append(o["bbapi"]["roster"]["player"])
            elif type(o["bbapi"]["roster"]["player"]) is list:
                # Multi player rosters
                roster = o["bbapi"]["roster"]["player"]
        except:
            sys.stderr.write("Not able to process roster {}\n".format(o))

        try:
            for player in roster:
                try:
                    if re.match(age_pattern, player["age"]) \
                            and int(player["skills"]["potential"]) >= min_potential \
                            and re.match(country_id_pattern, player["nationality"]['@id']) \
                            and int(player["salary"]) >= min_salary:
                        players.append(json.dumps(player))
                except:
                    sys.stderr.write("Not able to process player {}\n".format(player))
                    continue
        except:
            sys.stderr.write("Not able to process roster {}\n".format(o))
    return players


def get_players(s, ids):
    # player.aspx?playerid=43251670
    players = []
    total = len(ids)
    current = 0

    for player_id in ids:

        if use_random_sleeps:
            sec = randint(min_sleep, max_sleep)
            sleep(sec)

        url = base_url + "player.aspx?playerid=" + str(
            player_id)
        response = _get_(s, url)
        o = xmltodict.parse(response.text.encode('utf8'))

        current += 1
        progress_bar(
            "Getting players: Current player: {}".format(player_id),
            current, total)

        try:
            players.append(json.dumps(o["bbapi"]["player"]))
        except:
            sys.stderr.write("Not able to process player {}\n".format(o))
            continue

    return players


def save_players_to_tsv_file(players={}, file_path="players.tsv"):

    # format of player data
    # {"@id": "48638388", "firstName": "Igor", "lastName": "Bo\u0161i\u0107", "nationality": {"@id": "29", "#text": "Srbija"}, "age": "19", "height": "81", "dmi": "14000", "salary": "2618", "bestPosition": "C", "seasonDrafted": "50", "leagueDrafted": "1277", "teamDrafted": "42733", "draftPick": "16", "forSale": "0", "skills": {"gameShape": "7", "potential": "9"}}
    # {"@id": "48315767", "firstName": "Dragan", "lastName": "Preradovi\u0107", "nationality": {"@id": "29", "#text": "Srbija"}, "age": "19", "height": "82", "dmi": "196800", "salary": "6602", "bestPosition": "C", "seasonDrafted": "49", "leagueDrafted": "1281", "teamDrafted": "100575", "draftPick": "4", "forSale": "0", "skills": {"gameShape": "9", "potential": "9"}}

    player_base_url = "https://www2.buzzerbeater.com/player/"

    f = open(file_path, "w", encoding="UTF8")
    f.write("{}\tcountry\tsalary\tage\tpot\theight\tdmi\tseasonDrafted\tforSale".format(player_base_url) + "\n")

    for player in players:
        player_json = json.loads(player, encoding="utf8")

        gsheets_link = \
            "=HYPERLINK(CONCATENATE($A$1, \"{}\", \"/overview.aspx\"),\"{} {}\")".format(
                player_json["@id"],
                player_json["firstName"],
                player_json["lastName"]
            )
        f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            # player_json["@id"],
            gsheets_link,
            player_json["nationality"]["#text"],
            player_json["salary"],
            player_json["age"],
            player_json["skills"]["potential"],
            # height is in inches and we are saving in cm: 1 in = 2.54 cm
            int(round(int(player_json["height"]) * 2.54, 0)),
            player_json["dmi"],
            player_json["seasonDrafted"],
            player_json["forSale"]
        ))

    # close the file
    f.close()


def save_players_to_tsv_files_by_country(players=[], file_name_prefix="players_by_country"):
    # format of player data
    # {"@id": "48638388", "firstName": "Igor", "lastName": "Bo\u0161i\u0107", "nationality": {"@id": "29", "#text": "Srbija"}, "age": "19", "height": "81", "dmi": "14000", "salary": "2618", "bestPosition": "C", "seasonDrafted": "50", "leagueDrafted": "1277", "teamDrafted": "42733", "draftPick": "16", "forSale": "0", "skills": {"gameShape": "7", "potential": "9"}}
    # {"@id": "48315767", "firstName": "Dragan", "lastName": "Preradovi\u0107", "nationality": {"@id": "29", "#text": "Srbija"}, "age": "19", "height": "82", "dmi": "196800", "salary": "6602", "bestPosition": "C", "seasonDrafted": "49", "leagueDrafted": "1281", "teamDrafted": "100575", "draftPick": "4", "forSale": "0", "skills": {"gameShape": "9", "potential": "9"}}

    player_base_url = "https://www2.buzzerbeater.com/player/"

    out_files = {}
    for player in players:
        player_json = json.loads(player, encoding="utf8")
        nationality_id = player_json["nationality"]["@id"]

        f = out_files.get(nationality_id, None)
        if f is None:
            f = open(file_name_prefix + "_{}.tsv".format(nationality_id), "w", encoding="UTF8")
            f.write(
                "{}\tcountry\tsalary\tage\tpot\theight\tdmi\tseasonDrafted\tforSale".format(
                    player_base_url) + "\n")
            out_files.update({nationality_id: f})

        gsheets_link = \
            "=HYPERLINK(CONCATENATE($A$1, \"{}\", \"/overview.aspx\"),\"{} {}\")".format(
                player_json["@id"],
                player_json["firstName"],
                player_json["lastName"]
            )
        f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            # player_json["@id"],
            gsheets_link,
            player_json["nationality"]["#text"],
            player_json["salary"],
            player_json["age"],
            player_json["skills"]["potential"],
            # height is in inches and we are saving in cm: 1 in = 2.54 cm
            int(round(int(player_json["height"]) * 2.54, 0)),
            player_json["dmi"],
            player_json["seasonDrafted"],
            player_json["forSale"]
        ))

    # close opened files
    for key, file in out_files.items():
        out_files.get(key).close()


def progress_bar(title, current, total, bar_length=20):
    percent = float(current) * 100 / total
    arrow = '-' * int(percent / 100 * bar_length - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    # print('Scouting teams progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
    sys.stdout.write("\r{}: [{}] {}%".format(title, arrow + spaces,
                                             int(round(percent))))
    sys.stdout.flush()
    if percent == 100:
        sys.stdout.write("\n")


def _get_(s, url):
    if use_random_sleeps:
        sec = randint(min_sleep, max_sleep)
        sleep(sec)

    return s.get(url)
