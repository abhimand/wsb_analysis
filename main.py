# Probs should write this in a readme but this will have to do. 
# Basically I had a choice of using beautiful soup vs selenium to web scrap and I end up choosing this tutorial
# There were two reasons: 
# 1. For beautiful soup, connection was often interrupted for some reason either poor interent connect or some networking issue
# 2. There was this wonderful yet incomplete tutorial that proves selenium is far more useful as it can start up it's own chrome driver and i can just read from it
# This will eventually get depracated as reddit updates and upgrade. But for now, we shall just use this. 

from selenium import webdriver
from collections import Counter
import numpy as np
from datetime import date,timedelta
from dateutil.parser import parse 
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json


def grab_html():
    url = 'https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Daily%20Discussion%22&restrict_sr=1&sort=new'
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    return driver

def grab_stocklist():
    with open('stockslist.txt', 'r') as w:
        stocks = w.readlines()
        stocks_list = []
        for a in stocks:
            a = a.replace('\n','')
            stocks_list.append(a)
    return stocks_list

def grab_link(driver, specified_text, time):
    links = driver.find_elements_by_xpath('//*[@class="_eYtD2XCVieq6emjKBH3m"]')
    for a in links:
        if a.text.startswith(specified_text): # daily discussion link
            date = ''.join(a.text.split(' ')[-3:])
            parsed = parse(date) 
            if parse(str(time)) == parsed:
                link = a.find_element_by_xpath('../..').get_attribute('href')
                print(link)
    stock_link = link.split('/')[-3]
    driver.close() 
    return stock_link

def grab_commentid_list(stock_link):
    print(stock_link)
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{stock_link}')
    print(html)
    raw_comment_list = html.json()
    print(raw_comment_list)
    return raw_comment_list


def get_comments(comment_list):
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search?ids={comment_list}&fields=body&size=1000')
    newcomments = html.json()
    return newcomments

def get_stock_list(newcomments,stocks_list, dict):
    for a in newcomments['data']:
        for ticker in stocks_list:
            if ticker in a['body']:
                dict[ticker]+=1

if __name__ == "__main__":

    # dates
    tomorrow = date.today() + timedelta(days=1)
    today = date.today() + timedelta(days=0)
    yesterday = date.today() - timedelta(days=1)

    # Daily Discussion
    daily_stock_dict = Counter()
    daily = 'Daily Discussion Thread'

    # What Are Your Moves
    moves_stock_dict = Counter()
    moves = 'What Are Your Moves'

    # Set-up
    driver = grab_html() # pretty much starts the selenium driver with link - > web scraps the daily discusison and what are your movies search flair
    stocks_list = grab_stocklist() # grab list of stock tickers from rudimentary list - which btw the tutorial did not provide, and this list does not contain all tickers like GME, PLTR, etc  
    
    # What Are Your Moves - Yesterday
    # stock_link = grab_link(driver, moves, yesterday) # finds the link for yesterday 
    # comment_ids_list = grab_commentid_list(stock_link) # provides list of all comments based on yesterday's link
    # for comment_id in comment_ids_list['data']:
    #     c = get_comments(comment_id)
    #     print(c)
    #     get_stock_list(c,stocks_list, moves_stock_dict)
    #     print(moves_stock_dict)
    #     with open(moves + '_' + str(tomorrow) + '_ticks.txt', 'w') as file:
    #         file.write(json.dumps(moves_stock_dict))       

    # Daily Discussion - Yestereday
    stock_link = grab_link(driver, daily, yesterday) # finds the link for yesterday 
    comment_ids_list = grab_commentid_list(stock_link) # provides list of all comments based on yesterday's link
    for comment_id in comment_ids_list['data']:
        c = get_comments(comment_id)
        get_stock_list(c,stocks_list, daily_stock_dict)
        with open(daily + '_' + str(yesterday) + '_ticks.txt', 'w') as file:
            file.write(json.dumps(daily_stock_dict))        