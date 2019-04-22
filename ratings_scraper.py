import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from time import sleep

def update_ratings():
    url = 'http://clubelo.com/Ranking'
    # instantiate a chrome options object so you can set the size and headless preference"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920x1080')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    sleep(1)

    rating_df = pd.read_html(driver.page_source,match='Club')[0]
    rating_df.columns = rating_df.iloc[0]
    rating_df = rating_df.iloc[1:]
    rating_df.loc[:,'Club'] = rating_df['Club'].str.replace('^\d+', '').str.strip()
    rating_df['Elo'] = pd.to_numeric(rating_df['Elo'])
    rating_df['date'] = str(datetime.datetime.now())
    rating_df[['Club','Elo','date']].to_csv('data/ratings_latest.csv',index=False)
    
    print('Done!')
    
def filter_ratings(ratings_df, team_list):
    return (
    ratings_df.loc[ratings_df.Club.isin(team_list),
                   ['Club','Elo']].set_index('Club')['Elo'].to_dict())