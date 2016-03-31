import argparse
import requests
import collections
from lxml import html
import csv
import logging


logger = logging.getLogger('retrieve_players_stats')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()

# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)



BASE_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

players_counter = 0

def retrieve_players_stats( game_id, data_dir ):

    url = BASE_URL.format(game_id)

    try:
        logger.debug("Getting url %s, counter %s", url, players_counter)
        request = requests.get(url)
    except:
        logger.error ("Error retrieving URL: %s", url)
        return

    tree = html.fromstring(request.text)

    player_stats_list = list()

    for team in tree.xpath('//div[@id="gamepackage-box-score"]/article/div[@id="gamepackage-boxscore-module"]/div[@class="row-wrapper"]/div/div[@class="sub-module"]/div[@class="content hide-bench"]'):

        for index, player_table in enumerate(team.xpath('table/tbody')):

            for player in player_table.xpath('tr[not(@class="highlight")]'):

                try:
                    player_stats = collections.OrderedDict()
                    player_stats['GAME_ID']= game_id

                    player_stats['TEAM']=team.xpath('div[@class="table-caption"]/text()')[0].strip()
                    player_stats['NAME']=player.xpath('td[@class="name"]/a/text()')[0].strip()
                    player_stats['POSITION']=player.xpath('td[@class="name"]/span[@class="position"]/text()')[0].strip()
                    player_stats['STARTER']=team.xpath('table/thead/tr/th[@class="name"]/text()')[index].strip() == 'starters'

                    player_stats['MIN']=player.xpath('td[@class="min"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['FG']=player.xpath('td[@class="fg"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['3PT']=player.xpath('td[@class="3pt"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['FT']=player.xpath('td[@class="ft"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['OREB']=player.xpath('td[@class="oreb"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['DREB']=player.xpath('td[@class="dreb"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['REB']=player.xpath('td[@class="reb"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['AST']=player.xpath('td[@class="ast"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['STL']=player.xpath('td[@class="stl"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['BLK']=player.xpath('td[@class="blk"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['TO']=player.xpath('td[@class="to"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['PF']=player.xpath('td[@class="pf"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['+/-']=player.xpath('td[@class="plusminus"]/text()|td[@class="dnp"]/text()')[0].strip()
                    player_stats['PTS']=player.xpath('td[@class="pts"]/text()|td[@class="dnp"]/text()')[0].strip()

                    player_stats_list.append(player_stats)
                except:
                    logger.error ("Error retrieving data for game: %s",game_id)
                    pass


    if player_stats_list :
        with open(str(data_dir)+ '/players_'+str(game_id)+'.csv', 'wb') as f:
            w = csv.DictWriter(f, player_stats_list[0].keys())
            w.writeheader()

            for player_stats in player_stats_list:
                w.writerow(player_stats)

        logger.info ("Finished retrieving data for game: %s",game_id)


def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory', required=True)
    parser.add_argument('--game_id', help='game id', required=False)
    parser.add_argument('--start_rec_ind', help='game id', required=False, default=1, type=int)
    parser.add_argument('--end_rec_ind', help='game id', required=False, default=100000, type=int)
    args = parser.parse_args()


    if args.game_id != None :
        retrieve_players_stats(args.game_id, args.data_dir)

    else:
        global  players_counter

        with open(args.data_dir+'/games.csv', 'rb') as gamesfile:
            games_reader = csv.DictReader(gamesfile)
            next(games_reader, None)    #skip header

            for row in games_reader:
                players_counter += 1

                if (players_counter >= args.start_rec_ind and players_counter <= args.end_rec_ind) :
                    game_id = row['GAME_ID']
                    if (game_id != 'NA'):
                        retrieve_players_stats(game_id, args.data_dir)


if __name__ == "__main__":
    main()