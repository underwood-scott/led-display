from datetime import datetime, timedelta
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import requests


def get_current_games(sport, teams, utc_offset):
    urls = {'nfl': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
            'nba': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
            'ncaafb': 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
            'ncaabb': 'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
            'mlb': 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard'}

    response = requests.get(urls[sport])
    games = []
    todays_date = datetime.now()
    for event in response.json()['events']:
        event_date = datetime.strptime(event['date'], '%Y-%m-%dT%H:%MZ') + timedelta(hours=utc_offset)
        for team in teams:
            if team in event['name'] and event_date.date() == todays_date.date():
                competition = event['competitions'][0]
                # store general game info
                game = {'time': event_date.time(), 
                        'status': event['status']['type']['name'],
                        'clock': event['status']['displayClock'],
                        'period': event['status']['period'],
                        'sport': sport,
                        'name': event['name']}
                if sport == 'nfl' or sport == 'ncaafb':
                    game['down'] = competition.get('situation', {}).get('shortDownDistanceText'),
                    game['spot'] = competition.get('situation', {}).get('possessionText'),
                    game['possession'] = competition.get('situation', {}).get('possession')
                # store the individual team info
                for competitor in competition['competitors']:
                    if competitor['homeAway'] == 'home':
                        game['home_location'] = competitor['team']['location']
                        game['home_team'] = competitor['team']['name']
                        game['home_logo'] = competitor['team']['logo']
                        game['home_score'] = competitor['score']
                        game['home_abbreviation'] = competitor['team']['abbreviation']
                        game['home_color'] = competitor['team']['color']
                    else:
                        game['away_location'] = competitor['team']['location']
                        game['away_team'] = competitor['team']['name']
                        game['away_logo'] = competitor['team']['logo']
                        game['away_score'] = competitor['score']
                        game['away_abbreviation'] = competitor['team']['abbreviation']
                        game['away_color'] = competitor['team']['color']

                games.append(game)

    return games


def update_game(game):
    urls = {'nfl': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
            'nba': 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
            'ncaafb': 'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
            'ncaabb': 'https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
            'mlb': 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard'}

    response = requests.get(urls[game['sport']])
    for event in response.json()['events']:
        if event['name'] == game['name']:
            competition = event['competitions'][0]
            update = {'clock': event['status']['displayClock'],
                    'period': event['status']['period']}
            for competitor in competition['competitors']:
                if competitor['homeAway'] == 'home':
                    update['home_score'] = competitor['score']
                else:
                    update['away_score'] = competitor['score']

    return update


if __name__ == '__main__':
    UTC_OFFSET = -5
    NFL_TEAMS = ['Green Bay Packers', 'Washington Commanders']
    NBA_TEAMS = ['Milwaukee Bucks', 'Cleveland Cavaliers']
    NCAAFB_TEAMS = ['Wisconsin Badgers']
    NCAABB_TEAMS = ['Wisconsin Badgers', 'Marquette Golden Eagles']
    MLB_TEAMS = ['Milwaukee Brewers', 'Chicago Cubs']


    nfl_games = get_current_games('nfl', NFL_TEAMS, UTC_OFFSET)
    print(nfl_games)

