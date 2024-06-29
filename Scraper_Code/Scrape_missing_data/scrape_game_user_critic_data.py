# Credit to Author https://github.com/GregorUT 
# for original scraper code and providing 
# original Kaggle Dataset of vgchartz 

from bs4 import BeautifulSoup, element
import urllib
import pandas as pd
import numpy as np

from http.client import IncompleteRead
from requests.exceptions import HTTPError

from time import sleep

def read_url(url_link:str):
    reread_max = 5

    retry_delay = 1
    reread_count = 0

    got_or_no_data = False    
    read_data = ''
    while not got_or_no_data:
        try:
            read_data = urllib.request.urlopen(url_link).read()
            got_or_no_data = True
        except IncompleteRead as e:
            # Handle the incomplete read exception
            print(f"IncompleteRead error occurred: {e}: ", end='')
            if reread_count < reread_max:
                print('retrying to read...')
                reread_count += 1
                sleep(.5 * reread_count)
            else:
                print('too many reread attempts, skipping...') 
                got_or_no_data = True
        except Exception as ex:
            if 'HTTP Error 429' in str(ex):
                print(f"HTTP Error 429: Too Many Requests. Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            # Handle other exceptions
            print(f"An unexpected error occurred: {ex}")
            got_or_no_data = True

    return read_data

def scrape_vg_missing_data(page:int, results_chunk:int):
    rec_count = (page-1) * results_chunk
    rank = []
    gname = []
    critic_score = []
    user_score = []

    urlhead = 'http://www.vgchartz.com/gamedb/?page='
    urltail = '&console=&region=All&developer=&publisher=&genre=&boxart=Both&ownership=Both'
    urltail += f'&results={results_chunk}&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0'
    urltail += '&showpublisher=1&showvgchartzscore=0&shownasales=1&showdeveloper=1&showcriticscore=1'
    urltail += '&showpalsales=0&showpalsales=1&showreleasedate=1&showuserscore=1&showjapansales=1'
    urltail += '&showlastupdate=0&showothersales=1&showgenre=1&sort=GL'

    surl = urlhead + str(page) + urltail
    r = read_url(surl)
    if r == '': 
        print(f"page #{page+1} couldn't be read: skipping...")
        return 
    
    soup = BeautifulSoup(r,features="html.parser")
    print(f"Page: {page}")

    # search for <a> tags with game urls
    game_tags = list(filter(
        lambda x: 'href' in x.attrs and x.attrs['href'].startswith('https://www.vgchartz.com/game/'),
        soup.find_all("a")
    ))

    rec_list = list(range(rec_count, rec_count + len(game_tags)))
    for record_num, tag in zip(rec_list, game_tags):

        # get game name (to merge on)
        game_name = " ".join(tag.string.split())
        print(f"{record_num + 1} Fetch data for game {game_name}", end='')
        
        data = tag.parent.parent.find_all("td")
        game_rank = np.int32(data[0].string)
        
        game_critic_score = (data[6].string) if not data[6].string.startswith("N/A") else np.nan
        game_user_score = (data[7].string) if not data[7].string.startswith("N/A") else np.nan
     
        sale_na = float(data[9].string[:-1]) if not data[9].string.startswith("N/A") else np.nan
        sale_eu = float(data[10].string[:-1]) if not data[10].string.startswith("N/A") else np.nan
        sale_jp = float(data[11].string[:-1]) if not data[11].string.startswith("N/A") else np.nan
        sale_ot = float(data[12].string[:-1]) if not data[12].string.startswith("N/A") else np.nan
        
        # if there isn't any sales data, skip it
        not_na = lambda x: str(x) != 'nan'
        has_sales = [not_na(sale_na), not_na(sale_eu),\
                        not_na(sale_jp), not_na(sale_ot)]
        if not any(has_sales):
            print(': No sales data, skip...')
            continue
        print('\n',end='')

        # go to every individual game's info page to get genre info
        url_to_game = tag.attrs['href']
        game_info_page = read_url(url_to_game)
        if game_info_page == '': # if can't read game page: skip game entry
            print(f"{url_to_game} can't be read: skipping...") 
            continue
        
        gname.append(game_name)
        rank.append(game_rank)

        critic_score.append(game_critic_score)
        user_score.append(game_user_score)

    columns = {
        'Rank': rank,
        'Name': gname,
        'Critic_Score': critic_score,
        'User_Score': user_score
    }

    df = pd.DataFrame(columns)
    print(df.head(1))

    return df