#!/usr/bin/env python
import sys, os, time, urllib, urllib.request, shutil, re, lxml, threading, queue, multiprocessing
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of

# 2015Webcast.py gets all the information for 2016 webcasts in the following format:
# name, youtubeUp, sha256, dir, vidlink
# and stores the information into a csv format in a text file

#TODO youtube-Upload: unlisted, no votes, comments disabled... anything else?
#url = "http://matterhorn2-player-1.lt.ucsc.edu:8080/engage/ui/index.html" #2015

# init()
def init():
    # 2016 webcast gallery link
    root_url = "http://matterhorn-player-1.lt.ucsc.edu:8080/engage/ui/index.html"
    # load chrome webdriver
    chrome = webdriver.Chrome()
    chrome.get(root_url)

    return chrome

# Open next page
def next_page(chrome, wait):
    try:
        # next button clickable
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Next')))
        chrome.find_element_by_link_text("Next").click() # click next button
    except Exception as e:
        print("next_page error:", e, flush=True)
        return 1
    else:
        return 0


def get_webcast_list(src):
    webcastlist = []
    html = BeautifulSoup(src, 'lxml')
    for table in html.find_all('table'):
        for a_tag in table.find_all('a'):
            if a_tag.text != "":
                # adds (title, link) to webcastlist
                title = a_tag.text
                link = real_link(a_tag.get('href'))
                info = (title, link)
                webcastlist.append(info)

    return webcastlist

def real_link(suffix):
    base_url = "http://matterhorn-player-1.lt.ucsc.edu:8080/engage/ui/"
    return base_url + suffix

# main
def main(argv):
    chrome = init()

    # max time out = 60 seconds
    wait = WebDriverWait(chrome, 60)

    time.sleep(5)

    file = open('links.txt', 'a')

    while True:
        info = get_webcast_list(chrome.page_source)

        for title, link in info:
            file.write(title + ', ' + link + '\n')
            print('writing...\n' + title + ', ' + link + '\n', flush=True)

        if next_page(chrome, wait) == 1:
            break;
        else:
            time.sleep(3)

    file.close()
    chrome.close()

if __name__ == "__main__":
    main(sys.argv[1:])
