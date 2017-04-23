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
# urllib.request.urlretrieve("http://matterhorn2-player-1.lt.ucsc.edu:8080/static/engage-player/284481fd-9ca3-4407-805a-b03674f74173/6cd65e61-2119-42a0-a7d8-07d84c26e8a8/screen_secondary.mp4", "TestGet")

WEBCAST_URL = "https://webcast.ucsc.edu/"
#WEBCAST_URL = "http://facebook.com"

# Gets (titles, url) for each table element
def getCourselist(source):
    courselist = []
    html = BeautifulSoup(source, "lxml")
    for table in html.find_all("table"): #NOTE: more than one table? prob not
        for row in table.find_all("tr"):
            course = ()
            for td_tag in row.find_all("td"):
                if td_tag.a is None:
                    course += (td_tag.text,)
                else:
                    course += (td_tag.a.get("href"),)

            courselist.append(course)
    return courselist

def getWebcastlist(source):
    webcastlist = []
    html = BeautifulSoup(source, "lxml")
    for table in html.find_all("table"):
        for a_tag in table.find_all("a"):
            if a_tag.text != "":
                webcast = (a_tag.text, a_tag.get("href"))
                webcastlist.append(webcast)

    return webcastlist

def addWebcastVidTask(download_list, chrome, title):
    download_tag = chrome.find_element_by_id("oc_download_video")
    x = 0
    for a_tag in download_tag.find_elements_by_tag_name("a"):
        link = a_tag.get_attribute("href")
        if link.endswith(".mp4"):
            file_name = title + " - " + str(x) + ".mp4"
            for (video, link) in download_list:
                if file_name == video:
                    x += 1 # webcast might have split screen
                    file_name = title + " - " + str(x) + ".mp4"

            download_list.append((file_name, link))
            #ve(link, title + " - " +  str(x) + ".mp4")

def webcast_worker(task):
    (title, url) = task
    print("Downloading %s..." % (title), flush=True)
    try:
        urllib.request.urlretrieve(url, title)
        #shutil.move(title, directory)
    except Exception as e:
        print("webcast_worker error:", e, flush=True)

    print("Download complete for %s" % (title), flush=True)


def main(argv):
    # 1. Default site https://webcast.ucsc.edu/
    # if default site works
    # else ask user for webcast site
    # or press enter nothing exit
    try:
        sys.stdout.write("Connecting to " + WEBCAST_URL + "...")
        sys.stdout.flush()
        req = urllib.request.urlopen(WEBCAST_URL, timeout=10)
    except urllib.error.HTTPError as e:
        print("\nHttp error:", e)
        sys.exit()
    except urllib.error.URLError as e:
        print("\nURL error:", e)
        sys.exit()
    except:
        print("\nSomething has gone wrong")
        sys.exit()
    else:
        if req.getcode() == 200:
            sys.stdout.write("\rConnection to " + WEBCAST_URL + " was established\n")
            if req.geturl() != WEBCAST_URL:
                sys.stdout.write(WEBCAST_URL + " was redirected to " + req.geturl() + "\n")
                sys.stdout.flush()
                print("Would you still like to continue with", req.geturl(), "? (Y/N)")
                i = input()
                if i.lower() == 'n':
                    print("Exiting script...")
                    sys.exit()

    # 2. Get current list of available webcast.
    # ask which to download (all available webcast videos for the course)
    ## download selected or just one of them
    # or download EVERYTHING

    courselist = getCourselist(req.read())
    numCourses = len(courselist)

    for x in range(numCourses):
        print('[', x, ']', courselist[x][0])

    # TODO add support for multiple course selection
    print("\nChoose a number and press enter")
    i = None
    while i is None or not(0 <= i and i < numCourses):
        try:
            i = int(input())
        except ValueError:
            print("Not a number")
        except:
            print("Not a valid input")

            # Make directory for course

    sys.stdout.write("Retrieving video list...")
    try:
        webcast_req = urllib.request.urlopen(courselist[i][1], timeout=10)
    except urllib.error.HTTPError as e:
        print("\nHttp error:", e)
        sys.exit()
    except urllib.error.URLError as e:
        print("\nURL error:", e)
        sys.exit()
    except:
        print("\nSomething has gone wrong")
        sys.exit()
    else:
        sys.stdout.write("\rVideo list for " + courselist[i][0] + " retrieved\n")


    chrome = webdriver.Chrome()
    wait = WebDriverWait(chrome, 60)

    print("Chrome loaded", flush=True)

    webcastlist = getWebcastlist(webcast_req.read())
    download_list = []

    for title, url in webcastlist:
        try:
            #url_req = urllib.request.urlopen(url, timeout=10)
            chrome.get(url)
            wait.until(EC.element_to_be_clickable((By.ID, "oc_download-button")))
            chrome.find_element_by_id("oc_download-button").click()
            wait.until(EC.element_to_be_clickable((By.ID, "oc_download_video")))
        except urllib.error.HTTPError as e:
            print("\nHttp error:", e)
        except urllib.error.URLError as e:
            print("\nURL error:", e)
        except Exception as e:
            print("\nSomething has gone wrong for", e)
        else:
            addWebcastVidTask(download_list, chrome, title)

    chrome.close()
    mp = multiprocessing.Pool(2)
    mp.map(webcast_worker, download_list)

    print("Download complete")

    hashes = []

    # Compare hashes and remove duplicates
    for downloaded_file in download_list:
        (name, title) = downloaded_file
        sha256 = hashlib.sha256()
        print(name)
        if os.path.exists(name):
            with open(name, 'rb') as content_file:
                while True:
                    content = content_file.read(1000000)
                    if not content:
                        break
                    sha256.update(content)

            if sha256.hexdigest() in hashes:
                os.remove(name)
            else:
                hashes.append(sha256.hexdigest())


if __name__ == "__main__":
    main(sys.argv[1:])
