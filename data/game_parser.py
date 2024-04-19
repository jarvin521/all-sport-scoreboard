import requests
import datetime
import time as t
#from utils import convert_time

URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard", \
    "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard" ]

#URLs = ["http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"]
def get_all_games():
    # for i in range(5):
    try:
        games = []
        for URL in URLs:
            response = requests.get(URL)    
            res = response.json()
            # i = 0
            for g in res['events']:
                info = g['competitions'][0]
                odds = info.get('odds', [{}])[0]
                if "nfl" in URL: 
                    if "Cincinnati Bengals" in g['name'] or "Minnesota Vikings" in g['name']:                       
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'nfl',
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
                    if "Kentucky Wildcats" in g['name'] or "adsf" in g['name']:    
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa',
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
                    if " " in g['name']:                       
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'nba',
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
                    if "Kentucky Wildcats" in g['name']: # or " " in g['name']:                     
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'ncaa', 
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
                    if "Reds" in g['name'] or " " in g['name']:
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'mlb',
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
                    if "asdf" in g['name']:
                        game = {'name': g['shortName'], 'date': g['date'], 'league': 'nhl', 
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
                    # i += 1
        return games
    except requests.exceptions.RequestException as e:
        print("Error encountered getting game info, can't hit ESPN api, retrying")
        # if i < 4:
        #     t.sleep(1)
        #     continue
        # else:
        #     print("Can't hit ESPN api after multiple retries, dying ", e)
    except Exception as e:
        print("something bad?", e)
