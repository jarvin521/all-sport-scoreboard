import requests
import json
import time as t
#from utils import convert_time

URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100", #NCAA Tournament
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200", #D1-FCS
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=81&limit=200", #D1-FBS
        "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
        'http://site.api.espn.com/apis/site/v2/sports/golf/leaderboard'
        ]

# URLs = ["http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50", #All D-1
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=23", #SEC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=2", #ACC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=8", #Big 12
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=4", #Big East
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=7" #Big Ten
#        ]

conferences = [] #["Favorites", "SEC"]
with open("ncaaf_conferences.json", "r") as json_file:
    ncaaf_json = json.load(json_file)

#Collect properties that are common to all sports
def create_game(g, info, league, sport, extra_fields=None):
    game = {
        'name': g['shortName'],
        'date': g['date'],
        'league': league,
        'sport': sport,
        'hometeam': info['competitors'][0]['team']['abbreviation'],
        'homeid': info['competitors'][0]['id'],
        'homescore': int(info['competitors'][0]['score']),
        'awayteam': info['competitors'][1]['team']['abbreviation'],
        'awayid': info['competitors'][1]['id'],
        'awayscore': int(info['competitors'][1]['score']),
        'time': info.get('status', {}).get('displayClock'),
        'quarter': info['status']['period'],
        'over': info['status']['type']['completed'],
        'state': info['status']['type']['state'],
        'stateDetail': info['status']['type']['shortDetail']
    }
    if extra_fields:
        game.update(extra_fields)
    return game

#Collect properties that are specific to baseball
def get_baseball_extra_fields(info):
    return {
        '1b': info.get("situation", {}).get("onFirst"),
        '2b': info.get("situation", {}).get("onSecond"),
        '3b': info.get("situation", {}).get("onThird"),
        'balls': info.get('situation', {}).get('balls'),
        'strikes': info.get('situation', {}).get('strikes'),
        'outs': info.get('situation', {}).get('outs')
    }

def get_golf(g, info, league, sport):
    game = {
        'name': g['shortName'],
        'date': g['date'],
        'league': league,
        'sport': sport,
        'state': info['status']['type']['state'],
        'stateDetail': info['status']['type']['shortDetail']
    }
    #top_three = sorted(info['competitors'], key=lambda x: x['position']['id'])[:3]
    top_nine = sorted([competitor for competitor in info['competitors'] if int(competitor['status']['position']['id']) > 0], key=lambda x: int(x['status']['position']['id']))[:9]
    leader_scores = []
    for i in top_nine:
        # Get the latest finished round number
        if info['status']['period'] == 5:
            latest_round = 4
        else:
            latest_round = int(info['status']['period'])  # Assuming 'round' is available and represents the latest finished round

        leader_scores.append({
            'golfer': i['athlete']['shortName'],
            'score': i['statistics'][0]['displayValue'],
            'hole': i['status']['thru'],
            'today_score': int(i ['linescores'][latest_round - 1]['value'])
        })
    
    # Add the leader_scores array to the game dictionary
    game['leader_scores'] = leader_scores
    return game

def get_all_games():
    for i in range(5):
        try:
            games = []
            for URL in URLs:
                response = requests.get(URL)
                res = response.json()
                for g in res['events']:
                    info = g['competitions'][0]
                    if "nfl" in URL:
                        if "~" in g['name']: #or " " in g['name']:
                            game = create_game(g, info, 'nfl', 'football')
                            games.append(game)
                    if "college-football" in URL:
                        for conference in conferences:
                            for team in ncaaf_json[conference]:
                                if team in g['name']:
                                    game = create_game(g, info, 'ncaa', 'football')
                                    games.append(game)
                    if "nba" in URL:
                        if "~" in g['name']:
                            game = create_game(g, info, 'nba', 'basketball')
                            games.append(game)
                    if "mens-college-basketball" in URL:
                        if "~" in g['name']: 
                        #if any(conference in info.get('groups', {}).get('shortName', '') for conference in ["SEC", "Big East", "Big 12", "Big Ten", "ACC"]):
                            game = create_game(g, info, 'ncaa', 'basketball')
                            games.append(game)
                    if "mlb" in URL:
                        if " " in g['name'] or "Minnesota Twins" in g['name']:
                            game = create_game(g, info, 'mlb', 'baseball', get_baseball_extra_fields(info))
                            games.append(game)
                    if "college-baseball" in URL:
                        if "Kentucky Wildcats" in g['name']:
                            game = create_game(g, info, 'ncaa', 'baseball', get_baseball_extra_fields(info))
                            games.append(game)
                    if "nhl" in URL:
                        if "~" in g['name'] or "USA" in g['name']:
                            game = create_game(g, info, 'nhl', 'football')
                            games.append(game)
                    if "golf" in URL:
                        if "Masters" in g['name'] or "US Open" in g['name'] or "PGA Championship" in g['name'] or "Open Championship" in g['name']:
                            game = get_golf(g, info, 'pga', 'golf')
                            games.append(game)
            return games
        except requests.exceptions.RequestException as e:
            if i < 4:
                t.sleep(1)
                continue
            else:
                print("Can't hit ESPN api after multiple retries, dying ", e)
        except Exception as e:
            print("something bad?", e)
            #print(info)
            #print(game)
            # sleep 60 seconds
            t.sleep(60)