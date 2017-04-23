#!/usr/bin/env python
import sys, os, time 
import hashlib, csv

def incre_version(title):
    p = "version "
    pt1 = title.find(p) + len(p)
    o = ord(title[pt1]) + 1
    num = chr(o)
    title = title[:pt1] + num + ']'
    print(title)
    return title


file = open('CurrentWebcastsList2.txt', 'r')
new_file = open('CurrentWebcastsList3.txt', 'w')

file_reader = csv.reader(file, delimiter=',')

list = []
for row in file_reader:
    list.append(row)

new_list = []
for row in list:
    title = row[0]

    for xrow in new_list:
        while xrow[0] == title:
            title = incre_version(title)

    row[0] = title
    new_list.append(row)

for t in new_list:
    string = ''
    for i in range(len(t)):
        string = string + t[i] + ','

    string = string[:len(string)-1] + '\n'
    new_file.write(string)

file.close()
new_file.close()

file = open('CurrentWebcastsList2.txt', 'r')
new_file = open('CurrentWebcastsList3.txt', 'r')

count = 0
for row in file:
    count = count + 1

print(str(count))

count = 0
for row in new_file:
    count = count + 1

print(str(count))

file.close()
new_file.close()
