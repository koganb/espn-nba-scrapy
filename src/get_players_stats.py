import argparse
import requests
from requests.adapters import HTTPAdapter
import collections
from lxml import html
import csv
import re

BASE_URL = 'http://espn.go.com/nba/team/stats/_/name/{0}/year/{1}/{2}'

import re

SCORE_PATTERN = re.compile("^\d+-\d+$")
GAME_ID_PATTERN = re.compile("/nba/recap\?id=\d+")

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=20))

def retrieve_players_stats(year, team_pref1, team_pref2, data_dir, years_back):

    for y in range(year - years_back + 1, year + 1):
        player_stats_list = list()
        request = s.get(BASE_URL.format(team_pref1, y, team_pref2))
        tree = html.fromstring(request.text)

        stat_names = tree.xpath('//table[tr/td/text()="GAME STATISTICS"]/tr[@class="colhead"]/td/a/text()')

        for player_stat_row in tree.xpath('//table[tr/td/text()="GAME STATISTICS"]/tr[@class !="stathead" and @class!="colhead" and @class!="total"]'):

            player_stat_value_list = player_stat_row.xpath('td')

            if len(player_stat_value_list) !=0 :
                player_stats = collections.OrderedDict()

                player_stats['NAME'] = player_stat_value_list[0].xpath("a/text()")[0].strip()
                player_stats['ID'] = str(player_stat_value_list[0].xpath("a/@href")[0].strip()).split('/')[-2]
                player_stats['TEAM'] = team_pref2
                player_stats['PLAY_SEASON'] = str(y - 1) + '/' + str(y)

                for stat_name, stat in zip(stat_names, player_stat_value_list[1:]):
                    player_stats[stat_name] = stat.xpath("text()")[0]

                player_stats_list.append(player_stats)

        if player_stats_list :
            with open(str(data_dir)+ '/player_stat_'+str(team_pref1)+ '_' + str(y) + '.csv', 'wb') as f:
                w = csv.DictWriter(f, player_stats_list[0].keys())
                w.writeheader()

                for player_stats in player_stats_list:
                    w.writerow(player_stats)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory', required=True)
    parser.add_argument('--year', help='Year YYYY', required=True, type=int)
    parser.add_argument('--years_back', help='Number of years back from year argument to bring stats', required=False,
                        type=int, default=1)
    parser.add_argument('--team_pref1', help='Team pref1 ex.("bos")', required=False)
    parser.add_argument('--team_pref2', help='Team pref2 ex.("boston-celtics")', required=False)
    args = parser.parse_args()

    if (args.team_pref1 != None and args.team_pref2 != None):
        retrieve_players_stats(args.year, args.team_pref1, args.team_pref2, args.data_dir, args.years_back)

    else:
        with open(args.data_dir + '/teams.csv', 'rb') as teamsfile:
            games_reader = csv.DictReader(teamsfile)

            for row in games_reader:
                retrieve_players_stats(args.year, row['PREFIX_1'], row['PREFIX_2'], args.data_dir, args.years_back)


if __name__ == "__main__":
    main()
