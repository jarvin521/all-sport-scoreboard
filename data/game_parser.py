import requests
import json
import time as t
#from utils import convert_time

URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50", #All D-1
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200", #D1-FCS
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=81&limit=200", #D1-FBS
        "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
        ]

# URLs = ["http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50", #All D-1
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=23", #SEC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=2", #ACC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=8", #Big 12
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=4", #Big East
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=7" #Big Ten
#        ]

conferences = ["Favorites", "SEC"]
with open("ncaaf_conferences.json", "r") as json_file:
    ncaaf_json = json.load(json_file)

def get_all_games():
    for i in range(5):
        try:
            games = []
            for URL in URLs:
                response = requests.get(URL)
                res = response.json()
                for g in res['events']:
                    info = g['competitions'][0]
                    odds = info.get('odds', [{}])[0]
                    if "nfl" in URL:
                        if "~" in g['name']: #or " " in g['name']:
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'nfl', 'sport': 'football',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                                'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                                'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'),
                                'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
                            games.append(game)
                    if "college-football" in URL:
                        for conference in conferences:
                            for team in ncaaf_json[conference]:
                                if team in g['name']:
                                    game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa', 'sport': 'football',
                                        'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                        'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                        'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                                        'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                                        'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'),
                                        'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                                    if odds:
                                        game['overUnder'] = odds.get('overUnder')
                                        game['spread'] = odds.get('spread')
                                    else:
                                        game['overUnder'] = None
                                        game['spread'] = None
                                    games.append(game)
                    if "nba" in URL:
                        if "Minnesota Timberwolves" in g['name']:
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'nba', 'sport': 'basketball',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                                'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
                            games.append(game)
                    if "mens-college-basketball" in URL: 
                        if any(conference in info.get('groups', {}).get('shortName', '') for conference in ["SEC", "Big East", "Big 12", "Big Ten", "ACC"]):
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa', 'sport': 'basketball',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                                'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
                            games.append(game)
                    if "mlb" in URL:
                        if "~" in g['name'] or "~" in g['name']:
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'mlb', 'sport': 'baseball',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'quarter': info['status']['period'], '1b' :info.get("situation", {}).get("onFirst"), '2b': info.get("situation", {}).get("onSecond"), '3b': info.get("situation", {}).get("onThird"),
                                'balls': info.get('situation', {}).get('balls'), 'strikes': info.get('situation', {}).get('strikes'), 'outs': info.get('situation', {}).get('outs'),
                                'over': info['status']['type']['completed'],'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
                            games.append(game)
                    if "college-baseball" in URL:
                        if "~" in g['name']:
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa', 'sport': 'baseball',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'quarter': info['status']['period'], '1b' :info.get("situation", {}).get("onFirst"), '2b': info.get("situation", {}).get("onSecond"), '3b': info.get("situation", {}).get("onThird"),
                                'balls': info.get('situation', {}).get('balls'), 'strikes': info.get('situation', {}).get('strikes'), 'outs': info.get('situation', {}).get('outs'),
                                'over': info['status']['type']['completed'],'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
                            games.append(game)
                    if "nhl" in URL:
                        if "Minnesota Wild" in g['name']:
                            game = {'name': g['shortName'], 'date': g['date'], 'league': 'nhl', 'sport': 'hockey',
                                'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                                'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                                'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                                'state': info['status']['type']['state'], 'stateDetail': info['status']['type']['shortDetail']}
                            if odds:
                                game['overUnder'] = odds.get('overUnder')
                                game['spread'] = odds.get('spread')
                            else:
                                game['overUnder'] = None
                                game['spread'] = None
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
