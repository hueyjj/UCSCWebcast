#!/usr/bin/env python
import sys, os, time, urllib, urllib.request, shutil, re, lxml, threading, queue, multiprocessing
import hashlib, csv, time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of


def init():
    chrome = webdriver.Chrome()
    return chrome

def extract_webcast_url(url):
    # example: http://matterhorn2-player-1.lt.ucsc.edu:8080/static/engage-player/c7c78c3b-eca4-4d1f-98be-4a53dd71869b/4c0d1b58-61ff-48a5-aa89-40dcd5a58422/screen_primary.jpg
    p = "engage-player/"
    pt1 = url.find(p) + len(p) # first index of ID "c7c78..."
    url = url[pt1:]
    slash = url.find('/') # index before end of ID "...869b"
    url = url[:slash]     # new url with just id "c7c78...69b"

    return url

def get_webcast_links(chrome):
    base = "http://matterhorn2-player-1.lt.ucsc.edu:8080/engage/ui/player.html?id="
    list = []

    img_elements = chrome.find_elements_by_tag_name('img')
    for img_tag in img_elements:
        link = img_tag.get_attribute('src')

        if 'matterhorn2' in link and 'engage-player' in link:
            # print(link, flush=True)
            link = base + extract_webcast_url(link)
            list.append(link)

    return list


def main(argv):
    chrome = init()

    url = "http://matterhorn2-player-1.lt.ucsc.edu:8080/engage/ui/index.html"
    chrome.get(url)
    time.sleep(5)

    break_time = 3600 # 60 minutes
    initial_time = time.clock()
    while True:
        chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        final_time = time.clock()
        if final_time - initial_time >= break_time:
            break

    list = get_webcast_links(chrome)

    with open('2016webcastslinks.txt', 'a') as file:
        for link in list:
            file.write(link + '\n')

        file.close()

    chrome.close()


if __name__ == "__main__":
    main(sys.argv[1:])
