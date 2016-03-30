import argparse
import requests
import collections
from lxml import html
import csv

URL = 'http://espn.go.com/nba/teams'



def retrieve_teams_data(data_dir) :
    request = requests.get(URL)


    tree = html.fromstring(request.text)

    team_data_list = list()

    for division in tree.xpath('//div[@class="mod-container mod-open-list mod-teams-list-medium mod-no-footer"]'):
        for team in division.xpath('div[@class="mod-content"]/ul/li'):
            team_data = collections.OrderedDict()
            team_data['NAME'] =team.xpath('div/h5/a/text()')[0].strip()
            team_data['DIVISION'] =division.xpath('div[@class="mod-header stathead"]/h4/text()')[0].strip()
            url = team.xpath('div/h5/a/@href')[0].strip()
            team_data['PREFIX_1'] = url.split('/')[-2]
            team_data['PREFIX_2']  = url.split('/')[-1]

            team_data_list.append(team_data)

    if team_data_list :
        with open(str(data_dir)+ '/teams.csv', 'wb') as f:
            w = csv.DictWriter(f, team_data_list[0].keys())
            w.writeheader()

            for team_data in team_data_list:
                w.writerow(team_data)



def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory', required=True)
    args = parser.parse_args()

    retrieve_teams_data(args.data_dir)



if __name__ == "__main__":
    main()

# tables = soup.find_all('ul', class_='medium-logos')
#
# teams = []
# prefix_1 = []
# prefix_2 = []
# for table in tables:
#     lis = table.find_all('li')
#     for li in lis:
#         info = li.h5.a
#         teams.append(info.text)
#         url = info['href']
#         prefix_1.append(url.split('/')[-2])
#         prefix_2.append(url.split('/')[-1])
#
#
# dic = {'prefix_2': prefix_2, 'prefix_1': prefix_1}
# teams = pd.DataFrame(dic, index=teams)
# teams.index.name = 'name'
# print(teams)
# copper.save(teams, 'teams')

