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

def scrape_vg_chartz(page:int,results_chunk:int, debug=False):
    rec_count = results_chunk * (page - 1)
    rank = []
    gname = []
    platform = []
    year = []
    genre = []
    publisher = []
    sales_na = []
    sales_eu = []
    sales_jp = []
    sales_ot = []

    def log_data(page_num):
        count_data = str(page_num) + ', '+ str(rec_count) + ': '
        game_data = {'rank':rank[-1],'gname':gname[-1],'platform': platform[-1],
                        'year':year[-1],'genre':genre[-1],'publisher':publisher[-1],
                        'sales_na':sales_na[-1], 'sales_eu': sales_eu[-1],
                        'sales_jp':sales_jp[-1], 'sales_ot': sales_ot[-1]}
        
        mode = 'w' if page_num == 1 else 'a'
        with open('vg_log_file.txt', mode) as f:
            f.write(count_data+str(game_data))

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

    for tag in game_tags:
        # get game name
        game_name = " ".join(tag.string.split())
        print(f"{rec_count + 1} Fetch data for game {game_name}", end='')

        # get different attributes
        # traverse up the DOM tree to get game info
        data = tag.parent.parent.find_all("td")
        game_rank = np.int32(data[0].string)
        game_platform = data[3].find('img').attrs['alt']
        game_publisher = data[4].string
        
        rec_count += 1

        sale_na = float(data[9].string[:-1]) if not data[9].string.startswith("N/A") else np.nan
        sale_eu = float(data[10].string[:-1]) if not data[10].string.startswith("N/A") else np.nan
        sale_jp = float(data[11].string[:-1]) if not data[11].string.startswith("N/A") else np.nan
        sale_ot = float(data[12].string[:-1]) if not data[12].string.startswith("N/A") else np.nan
        
        # if there isn't any sales data, skip it
        not_na = lambda x: str(x) != 'nan'
        has_sales = [not_na(sale_na), not_na(sale_eu),\
                        not_na(sale_jp), not_na(sale_ot)]
        if not any(has_sales):
            print(': No sales data, skip')
            continue
        print('\n',end='')

        # go to every individual game's info page to get genre info
        url_to_game = tag.attrs['href']
        game_info_page = read_url(url_to_game)
        if game_info_page == '': # if can't read game page: skip game entry
            print(f"{url_to_game} can't be read: skipping...") 
            continue

        # append game info and sales
        gname.append(game_name)
        rank.append(game_rank)
        platform.append(game_platform)
        publisher.append(game_publisher)

        sales_na.append(sale_na)
        sales_eu.append(sale_eu)
        sales_jp.append(sale_jp)
        sales_ot.append(sale_ot)
        
        release_year = data[13].string.split()[-1]

        # years are in 2 digit format: need to convert to 4 digits
        if release_year.startswith('N/A'):
            year.append('N/A')
        else:
            if int(release_year) >= 75:
                year_to_add = np.int32("19" + release_year)
            else:
                year_to_add = np.int32("20" + release_year)
            year.append(year_to_add)

        # get genre data from game page url if we were able to fetch it
        sub_soup = BeautifulSoup(game_info_page, "html.parser")
        
        # the info box is inconsistent among games so we
        # have to find all the h2 and traverse from that to the genre name
        h2s = sub_soup.find("div", {"id": "gameGenInfoBox"}).find_all('h2')

        # make a temporary tag here to search for the one that contains
        # the word "Genre"
        temp_tag = element.Tag
        for h2 in h2s:
            if h2.string == 'Genre':
                temp_tag = h2
        genre.append(temp_tag.next_sibling.string)

        if debug: log_data(page+1)

    columns = {
        'Rank': rank,
        'Name': gname,
        'Platform': platform,
        'Year': year,
        'Genre': genre,
        'Publisher': publisher,
        'NA_Sales': sales_na,
        'EU_Sales': sales_eu,
        'JP_Sales': sales_jp,
        'Other_Sales': sales_ot,
    }
    print(rec_count)
    df = pd.DataFrame(columns)
    print(df.columns)
    df = df[[
        'Rank', 'Name', 'Platform', 'Year', 'Genre', 'Publisher',
        'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']]
    
    return df

