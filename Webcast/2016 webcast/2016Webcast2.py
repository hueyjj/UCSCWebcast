#!/usr/bin/env python
import sys, os, time, urllib, urllib.request, shutil, re, lxml, threading, queue, multiprocessing
import hashlib, csv
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

def get_vid_link(chrome, wait, link):
    # open link
    chrome.get(link)

    # wait until download button is clickable
    try:
        wait.until(EC.element_to_be_clickable((By.ID, 'oc_download-button')))
    except Exception as e:
        print("wait error exception")

    # sleep a bit
    # sys.stdout.write('sleeping for a minute...')
    # sys.stdout.flush()
    # time.sleep(60)
    # sys.stdout.write('\rdone sleeping...\r')
    # sys.stdout.flush()

    links = []

    # find all Presentation (.mp4) links and store them in list
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'oc_download_video')))
        wait.until(EC.presence_of_element_located((By.ID, 'oc_title-1')))
        download_tag = chrome.find_element_by_id("oc_download_video")
        title_tag = chrome.find_element_by_id("oc_title-1")
    except Exception as e:
        print("\nget_vid_link error:", e, flush=True)

        # # after 30 times, sleep a bit
        # x = 30
        # print("sleeping for 30 seconds...    ", end='', flush=True)
        # time.sleep(15)
        # print("\rdone sleeping               ", end='', flush=True)

        print("\rrefreshing page...          ", end='', flush=True)
        chrome.refresh()
        print("\rpage refreshed              ", end='', flush=True)

        print("\rtrying to find download and title tag again...", end='', flush=True)
        wait.until(EC.presence_of_element_located((By.ID, 'oc_download_video')))
        wait.until(EC.presence_of_element_located((By.ID, 'oc_title-1')))
        time.sleep(5)
        download_tag = chrome.find_element_by_id("oc_download_video")
        title_tag = chrome.find_element_by_id("oc_title-1")

        if download_tag != '' and title_tag != '':
            print("\rfound download and title tag        ", flush=True)
        else:
            print("\rdid NOT find download and title tag\n" +
                  "for link: " + link, flush=True)
    except:
        print("=======================================================\n" +
              "something weird happened here... please find out why...\n" +
              "link: " + link + "\n" +
              "=======================================================\n", flush=True)

    for a_tag in download_tag.find_elements_by_tag_name('a'):
        title = title_tag.get_attribute('innerText')
        link_text = a_tag.get_attribute('innerText')
        link = a_tag.get_attribute("href")
        if "Presentation" in link_text and link.endswith('mp4'):
            info = (title, link)
            links.append(info)

    return links



def main(argv):
    chrome = init()
    wait = WebDriverWait(chrome, 60)

    file = open('2016webcastslinks.txt', 'r')
    file2 = open('2016webcastslinks2.txt', 'a')

    # wait_a_bit = 300
    # count = 0
    for link in file.readlines():
        # if count >= 30:
        #     print("sleeping for a bit", flush=True)
        #     time.sleep(wait_a_bit)
        #     print("done sleep", flush=True)
        #     count = 0

        # count = count + 1

        vid_list = get_vid_link(chrome, wait, link)

        # numbering videos; more than one version of the same webcast
        for x in range(0, len(vid_list)):
            version = ' [version ' + str(x+1) + ']'
            title = vid_list[x][0]
            link = vid_list[x][1]
            info = title + version + ',' + link + '\n'
            print(info, end='', flush=True)
            file2.write(info)
            file2.flush()

    file.close()
    file2.close()
    chrome.close()


if __name__ == "__main__":
    main(sys.argv[1:])
