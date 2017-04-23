#!/usr/bin/env python
import queue, threading, time, subprocess

lock_file = open('lock_test.txt', 'w')
lock = threading.Lock()

def worker(i, q):
    while True:
        print("%d: Looking for next work" % i, flush=True)
        task = q.get()
        if task is None:
            print('worker %d: done' % (i), flush=True)
            break

        lock.acquire()

        print("%d: lock acquired" % i, flush=True)
        lock_file.write("thread " + str(i) + " wrote to file.\n")
        #time.sleep(6)

        lock.release()

        print("%d: %s task done" % (i, task), flush=True)
        q.task_done()

q = queue.Queue()
num_worker_threads = 2
threads = []

for i in range(num_worker_threads):
    t = threading.Thread(target=worker, args=(i, q))
    t.start()
    threads.append(t)

for i in range(5):
    task = 'task ' + str(i)
    q.put(task)


print("threadtest starting", flush=True)

q.join()

for i in range(num_worker_threads):
    q.put(None)

for t in threads:
    t.join()

print("threadtest done", flush=True)
