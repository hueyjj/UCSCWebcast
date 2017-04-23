#!usr/bin/env python
import csv

file = open('2016webcastslinks3.txt', 'r')
new_file = open('2016webcastslinks4.txt', 'w')
reader = csv.reader(file, delimiter=',')

for row in reader:
    if 'test'.lower() in row[0].lower() or 'unscheduled'.lower() in row[0].lower():
        pass
    else:
        string = ''
        for i in range(len(row)):
            string = string + row[i] + ','

        string = string[:len(string)-1] + '\n'

        new_file.write(string)
        print(string)



file.close()
new_file.close()

file = open('2016webcastslinks3.txt', 'r')
count = 0
for line in file:
    count += 1

print(count)


new_file = open('2016webcastslinks4.txt', 'r')
count = 0
for line in new_file:
    count += 1

print(count)
