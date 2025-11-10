import requests
import json
from datetime import datetime
from pytz import timezone
import time as t
from bs4 import BeautifulSoup
import re
#from utils import convert_time

URLs = ["http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=23", #SEC
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=2", #ACC
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=8", #Big 12
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=4", #Big East
        "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=7", #Big Ten
        #"http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100", #NCAA Tournament
        "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80&limit=200", #D1-FBS
        #"https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=81&limit=200", #D1-FCS
        "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard",
        "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
        'http://site.api.espn.com/apis/site/v2/sports/golf/leaderboard',
        # "https://www.maxpreps.com/mn/jordan/jordan-hubmen-jaguars-panthers/football/schedule/",
        # "https://www.maxpreps.com/mn/east-grand-forks/east-grand-forks-green-wave/football/schedule/"
        ]

#URLs = [ "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=23" ]
#    "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50", #All D-1
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=23" #SEC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=2", #ACC
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=8", #Big 12
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=4", #Big East
#         "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=7" #Big Ten
#        ]

conferences = ["Favorites", "SEC"]
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

def create_prep_game(g, league, sport, extra_fields=None):
    game = {
        'name': f"{g['url_team']} vs. {g['opponent']}",
        'date': g['date'],
        'league': league,
        'sport': sport,
        'hometeam': g['url_team'] if g['home'] else g['opponent'],
        'homeid': g['url_team'] if g['home'] else g['opponent'],
        'homescore': int(g.get('home_score', 0)) if str(g.get('home_score', '')).isdigit() else 0,
        'awayteam': g['url_team'] if not g['home'] else g['opponent'],
        'awayid': g['url_team'] if not g['home'] else g['opponent'],
        'awayscore': int(g.get('away_score', 0)) if str(g.get('away_score', '')).isdigit() else 0,
        'state': "post" if g['time'] == "final" else "pre",
        'stateDetail': "final" if g['time'] == "final" else "pre"
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

def clean_opponent_name(raw_name):
    name = raw_name.lstrip('@').lstrip('vs').strip()
    name = re.sub(r'\*+$', '', name)
    if len(name) >= 2 and name[0] == name[1]:
        name = name[1:]
    return name

def parse_result(result_text):
    
    match = re.match(r'(W|L)(\d+)-(\d+)', result_text)
    
    if not match:
        return None
    outcome, score1, score2 = match.groups()
    score1, score2 = int(score1), int(score2)
    if outcome == 'W':
        return ('final', score1, score2)
    else:
        return ('final', score2, score1)

def get_maxpreps_schedule_json(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")
    
    # Extract the home team from the URL
    match = re.search(r'/mn/([^/]+)/', url)
    if not match:
        raise Exception(f"Could not parse home team from URL: {url}")
    url_team = match.group(1).replace('-', ' ').title()  # Convert to title case (e.g., "jordan" -> "Jordan")

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        raise Exception("No schedule tables found.")

    games = []
    current_year = datetime.now().year  # Get the current year to append to the MM/DD format
    central = timezone('US/Central')  # Define Central Time zone
    utc = timezone('UTC')
    for table in tables:
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            if not cells or len(cells) < 3:
                continue  # Skip empty or malformed rows

            date_str = cells[0]
            raw_opponent = cells[1]
            third_cell = cells[2]

            # Handle LIVE games
            if date_str.upper() == "LIVE":
                date_str = datetime.now().strftime("%m/%d")  # Use today's date
                time_str = "7:00PM"
                result = None
            # Handle past games with scores
            elif re.match(r'^[WL]\d+-\d+', third_cell):
                result = third_cell
                time_str = "7:00PM"  # Default time for past games
            # Handle future games with time
            else:
                result = None
                time_str = third_cell if re.match(r'\d{1,2}:\d{2}[ap]m', third_cell.lower()) else "7:00PM"

            try:
                naive_datetime = datetime.strptime(f"{date_str}/{current_year} {time_str}", "%m/%d/%Y %I:%M%p")
                datetime_obj = central.localize(naive_datetime).astimezone(utc)
            except ValueError:
                continue

            opponent = clean_opponent_name(raw_opponent)
            home = raw_opponent.startswith('vs')

            game = {
                "date": datetime_obj,
                "url_team": url_team,
                "opponent": opponent,
                "home": home
            }

            if result:
                parsed = parse_result(result)
                if parsed:
                    game["time"] = parsed[0]
                    game["home_score"] = parsed[1] if home else parsed[2]
                    game["away_score"] = parsed[2] if home else parsed[1]
            else:
                game["time"] = time_str

            games.append(game)

    # Find the game closest to the current date
    current_date = datetime.now(utc)
    closest_game = min(
        games,
        key=lambda game: abs(game['date'] - current_date)
    )
    # Format the date of the closest game as 'YYYY-MM-DDTHH:MMZ'
    closest_game['date'] = closest_game['date'].strftime('%Y-%m-%dT%H:%MZ')
    return closest_game

def get_all_games():
    for i in range(5):
        try:
            games = []
            for URL in URLs:
                if "maxpreps" in URL:
                    if "football" in URL:
                        sport = "football"
                    elif "basketball" in URL:
                        sport = "basketball"
                    g = get_maxpreps_schedule_json(URL)
                    game = create_prep_game(g, 'prep', sport)
                    games.append(game)
                else:
                    response = requests.get(URL)
                    res = response.json()
                    #list(res.keys())
                    for g in res['events']:
                        #list(g.keys())
                        info = g['competitions'][0]
                        if "nfl" in URL:
                            if " " in g['name']: #or " " in g['name']:
                                game = create_game(g, info, 'nfl', 'football')
                                games.append(game)
                        if "college-football" in URL:
                            for conference in conferences:
                                for team in ncaaf_json[conference]:
                                    if team in g['name']:
                                        game = create_game(g, info, 'ncaa', 'football')
                                        games.append(game)
                        if "nba" in URL:
                            if "Minnesota" in g['name']:
                                game = create_game(g, info, 'nba', 'basketball')
                                games.append(game)
                        if "mens-college-basketball" in URL:
                            if " " in g['name']: 
                            #if any(conference in info.get('groups', {}).get('shortName', '') for conference in ["SEC", "Big East", "Big 12", "Big Ten", "ACC"]):
                                game = create_game(g, info, 'ncaa', 'basketball')
                                games.append(game)
                        if "mlb" in URL:
                            if "~" in g['name']:
                                game = create_game(g, info, 'mlb', 'baseball', get_baseball_extra_fields(info))
                                games.append(game)
                        if "college-baseball" in URL:
                            if "~" in g['name']:
                                game = create_game(g, info, 'ncaa', 'baseball', get_baseball_extra_fields(info))
                                games.append(game)
                        if "nhl" in URL:
                            if "Minnesota Wild" in g['name'] or "USA" in g['name']:
                                game = create_game(g, info, 'nhl', 'football')
                                games.append(game)
                        if "golf" in URL:
                            if "Masters" in g['name'] or "US Open" in g['name'] or "PGA Championship" in g['name'] or "Open Championship" in g['name']:
                                game = get_golf(g, info, 'pga', 'golf')
                                games.append(game)
            #print(games)                    
            return games
        except requests.exceptions.RequestException as e:
            if i < 4:
                t.sleep(1)
                continue
            else:
                print("Can't hit ESPN api after multiple retries, dying ", e)
        except Exception as e:
            print("something bad?", e)
            # sleep 60 seconds
            t.sleep(60)