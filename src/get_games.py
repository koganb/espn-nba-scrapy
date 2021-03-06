import argparse
import requests
import collections
from lxml import html
import csv
import re


BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2/{2}'

import re
SCORE_PATTERN = re.compile("^\d+-\d+$")
GAME_ID_PATTERN = re.compile("/nba/recap\?id=\d+")

def retrieve_games_stats(year, team_pref1, team_pref2, data_dir, years_back):


    for y in range(year - years_back + 1 , year + 1 ) :

        game_stats_list = list()

        request = requests.get(BASE_URL.format(team_pref1, y, team_pref2))
        tree = html.fromstring(request.text)


        for game in tree.xpath('//div[@class="mod-container mod-table mod-no-header-footer"]/div[@class="mod-content"]/table/tr[not(@class="stathead") and not(@class="colhead")]'):

            if not game.xpath('td[@colspan="9"]') :  # game is not postponed

                game_stats = collections.OrderedDict()

                game_id_list = game.xpath('td/ul/li[@class="score"]/a/@href')
                game_stats['GAME_ID'] = game_id_list[0].split('=')[1] if (len(game_id_list) > 0 and GAME_ID_PATTERN.match(game_id_list[0])) else 'NA'

                game_date =  game.xpath('td[string-length( text()) > 7]/text()')[0].strip()
                month = game_date.split(' ')[1]
                weekday = game_date.split(' ')[0]
                if (month == 'Oct' or month == 'Nov' or month == 'Dec') :
                    game_stats['DATE'] = game_date.replace(weekday, '').strip() + ", " + str(y - 1)
                else:
                    game_stats['DATE'] = game_date.replace(weekday, '').strip() + ", " + str(y)

                game_stats['PLAY_SEASON'] = str(y - 1) + '/' + str(y)

                win_status = game.xpath('td/ul/li[contains(@class,"game-status")]/span/text()')[0].strip()
                home_or_visit = game.xpath('td/ul/li[@class="game-status"]/text()')[0].strip()
                opponent_team_href = game.xpath('td/ul/li[@class="team-name"]/a/@href')[0].strip()
                opponent_team = str(opponent_team_href).split('/')[-1]
                score = re.sub(' .*', '',game.xpath('td/ul/li[@class="score"]/a/text()')[0].strip())
                first_score = score.split('-')[0] if SCORE_PATTERN.match(score) else 'NA'
                second_score = score.split('-')[1] if SCORE_PATTERN.match(score) else 'NA'

                if home_or_visit == 'vs':   #list only home games
                    game_stats['HOME_TEAM'] = team_pref2
                    game_stats['VISIT_TEAM'] = opponent_team

                    if first_score == 'NA' or second_score == 'NA' :
                        game_stats['HOME_TEAM_SCORE'] = 'NA'
                        game_stats['VISIT_TEAM_SCORE'] = 'NA'

                    elif win_status == 'L':
                        game_stats['HOME_TEAM_SCORE'] = min(int(first_score), int(second_score))
                        game_stats['VISIT_TEAM_SCORE'] = max(int(first_score), int(second_score))

                    elif win_status == 'W':
                        game_stats['HOME_TEAM_SCORE'] = max(int(first_score), int(second_score))
                        game_stats['VISIT_TEAM_SCORE'] = min(int(first_score), int(second_score))

                    else:
                        raise Exception('Unknown winning status: ' + win_status )

                    game_stats_list.append(game_stats)

                # score_list[0] = re.sub('[^0-9-]', '', score_list[0]) # remove everething except hythen and numbers
                # game_stats['HOME_TEAM_SCORE'] = score_list[0].split('-')[0] if (len(score_list) > 0 and SCORE_PATTERN.match(score_list[0])) else 'NA'
                # game_stats['VISIT_TEAM'] = game.xpath('td/ul/li[@class="team-name"]/a/text()')[0].strip()
                # game_stats['VISIT_TEAM_SCORE'] = score_list[0].split('-')[1] if (len(score_list) > 0 and  SCORE_PATTERN.match(score_list[0])) else 'NA'





        if game_stats_list :
            with open(str(data_dir)+ '/games_'+str(team_pref1)+ '_' + str(y) + '.csv', 'wb') as f:
                w = csv.DictWriter(f, game_stats_list[0].keys())
                w.writeheader()

                for player_stats in game_stats_list:
                    w.writerow(player_stats)


def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory', required=True)
    parser.add_argument('--year', help='Year YYYY', required=True, type=int)
    parser.add_argument('--years_back', help='Number of years back from year argument to bring stats', required=False, type=int,default=1)
    parser.add_argument('--team_pref1', help='Team pref1 ex.("bos")', required=False)
    parser.add_argument('--team_pref2', help='Team pref2 ex.("boston-celtics")', required=False)
    args = parser.parse_args()

    if (args.team_pref1 != None and args.team_pref2 != None)  :
        retrieve_games_stats(args.year, args.team_pref1, args.team_pref2, args.data_dir, args.years_back)

    else:
         with open(args.data_dir+'/teams.csv', 'rb') as teamsfile:
            games_reader = csv.DictReader(teamsfile)

            for row in games_reader:
                retrieve_games_stats(args.year,  row['PREFIX_1'], row['PREFIX_2'], args.data_dir, args.years_back)

if __name__ == "__main__":
    main()