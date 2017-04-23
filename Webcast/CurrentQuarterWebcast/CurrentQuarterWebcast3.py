#!/usr/bin/env python
import sys, os, time, urllib, urllib.request, shutil, re, lxml, threading, queue, multiprocessing
import hashlib, csv, subprocess

def get_sha256(text):
    sha256 = hashlib.sha256()
    sha256.update(text.encode('utf-8'))
    return sha256.hexdigest()

def check_list(list, url):
    # check if sha256 of url matches a sha256 in the list
    # returns true if there's a match, false otherwise
    if list is None:
        return False

    for row in list:
        list_sha256 = row[0]
        if list_sha256 == get_sha256(url):
            return True
    return False

def youtube_upload(worker_num, lock, task_queue, file, log):
    # Worker thread function that will process each task in the queue
    # and will block if there are no items in the queue
    # Each task will download from a url and then upload to Youtube.
    # Thread will not get next task until its task is done
    while True:
        task = task_queue.get() # task = (title, url)
        time = time.strftime("%a, %d %b %Y %H:%M:%S")
        if task is None:
            print("%s %d: youtube_upload worker done" % (time, worker_num), flush=True)
            break;
        else:
            print("%s %d: working on %s" % (time, worker_num, task[0]), flush=True)

        # download video
        title = task[0]
        url = task[1]
        vid_title = title + '.mp4'
        try:
            urllib.request.urlretrieve(url, vid_title)
        except Exception as e:
            print("youtube_upload error: unable to download", title, url, flush=True)
            task_queue.task_done()
            continue

        # delete file if too small
        size = os.path.getsize(vid_title)
        if size <= 1000000: # delete < 1 MB file
            os.remove(vid_title)
            print("%d: removed (too small) %s" % (worker_num, vid_title), flush=True)
            task_queue.task_done()
            continue

        # upload to youtube
        tag_title = '--title={0:s}'.format(title)
        tag_privacy = "--privacy=unlisted"
        playlist = "2016_webcasts"
        tag_playlist = "--playlist=" + playlist
        youtube_upload = r"C:\users\jj\appdata\local\programs\python\Python35-32\Scripts\youtube-upload"
        retry_count = 0
        for attempt in range(20): # max 20 retry
            try:
                subprocess.run(['python', youtube_upload,
                                tag_title, tag_privacy, tag_playlist,
                                vid_title],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except subprocess.TimeoutExpired as e:
                print("%d: timeout (%d) while working on %s" %
                      (worker_num, attempt, vid_title), flush=True)
                retry_count += 1
                continue
            else:
                break

        # delete video from local storage
        if os.path.exists(vid_title):
            os.remove(vid_title)

        # return to start and get a new video
        if retry_count >= 20:
            print("%d: retry attempt MAXED out while working on %s" %
                  (worker_num, vid_title))
            log.write("never uploaded: " + vid_title + '\n')
            log.flush()
            continue

        # record video information
        lock.acquire()
        sha256 = get_sha256(url)
        video_info = "{0:s}, {1:s}, {2:s}\n".format(sha256, title, url)
        file.write(video_info)
        file.flush()
        lock.release()

        print("%s %d: uploaded %s" % (time, worker_num, vid_title))
        task_queue.task_done()

def main(argv):
    # MATH 3 LEC fall 2016 class- 30 [version 1],http://matterhorn2-player-1.lt.ucsc.edu:8080/static/engage-player/547a1471-4c04-491b-9448-6ab3a1079aea/6b7f3ad3-37b3-47ce-912b-c7585cae6cfd/screen_primary.mp4

    read_file = open('CurrentWebcastsList4.txt', 'r')
    log_file = open('log.txt', 'w')

    done_list = None
    if os.path.exists('Currentstorage.txt'):
        complete_file = open('Currentstorage.txt', 'r')
        done_reader = csv.reader(complete_file, delimiter=',')
        done_list = []
        for row in done_reader:
            done_list.append(row)

        complete_file.close()

    complete_file = open('Currentstorage.txt', 'a')

    # start a few threads
    lock = threading.Lock()
    task_queue = queue.Queue()
    workers = []
    num_worker = 5
    for i in range(num_worker):
        worker = threading.Thread(target=youtube_upload, args=(i, lock, task_queue, complete_file, log_file))
        worker.start()
        workers.append(worker)

    # read in list of videos
    invalid_links = []
    reader = csv.reader(read_file, delimiter=',')
    for row in reader: # row = [title, url]
        title = row[0]
        url = row[1]
        # throw away row[1] if it doesn't contain http or not .mp4 format i.e invalid element
        if 'http' not in url or url.endswith('mp4') is False:
            invalid_links.append((title, url))
            continue
        if check_list(done_list, url) is False:
            task_queue.put((title, url))
        else:
            print("%s already uploaded" % title)
            continue

    task_queue.join()

    for i in range(num_worker):
        task_queue.put(None)

    for worker in workers:
        worker.join()

    print("\nList of invalid links:")
    for i in range(len(invalid_links)):
        print(invalid_links[i][0], end=' ' )
        print(invalid_links[i][1])

    print("\nscript done.")

    read_file.close()
    complete_file.close()
    log_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
