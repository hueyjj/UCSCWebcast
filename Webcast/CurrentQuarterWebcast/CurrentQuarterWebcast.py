#!/usr/bin/env python
import sys, urllib.request, lxml
from bs4 import BeautifulSoup
from collections import OrderedDict

url = "https://webcast.ucsc.edu"
COURSE_LIST = "Course Webcast List"

def read_url(url):
    try:
        with urllib.request.urlopen(url) as f:
            content = f.read()
    except urllib.error.HTTPError:
        print("HTTPError:", url, flush=True)
        return None 
    return content

def filter_html(html):
    soup = BeautifulSoup(html, 'lxml')
    course_dir = []
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if "opencast" in href:
            course_dir.append(href)
    return course_dir

def find_webcasts(courses):
    webcasts = []
    for course in courses:
        html = read_url(course)
        if html is None:
            continue
        
        soup = BeautifulSoup(html, 'lxml')
        if soup.title.string == COURSE_LIST:
            for a_tag in soup.find_all('a'):
                href = a_tag.get('href')
                if "opencast" in href: # todo: possibly more error checking
                    webcasts.append(href)
        else:
            print("Has no webcasts:", course, flush=True)
            continue

    webcasts = remove_duplicates(webcasts) 
    return webcasts

def remove_duplicates(dup):
    return list(OrderedDict.fromkeys(dup))

def main():
    html = read_url(url)
    courses = filter_html(html)
    webcasts = find_webcasts(courses)
    with open("CurrentWebcastsList.txt", 'w') as f:
        for link in webcasts:
            f.write(link + '\n')
        f.close()
        
if __name__ == "__main__":
    main()
