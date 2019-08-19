#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Usage:
  redis-cluster-benchmark.py [--host <ip>] [-p <port>] [-n <request>] [-c <concurrent>] [--nocluster] [--timeit] [--pipeline] [--resetlastkey] [-h] [--version]

Options:
  --host <ip>        Redis server to test against [default: 127.0.0.1]
  -p <port>          Port on redis server [default: 7000]
  -n <request>       Request number [default: 100000]
  -c <concurrent>    Concurrent client number [default: 1]
  --nocluster        If flag is set then StrictRedis will be used instead of cluster lib
  --timeit           Run a mini benchmark to test performance
  --pipeline         Only usable with --timeit flag. Runs SET/GET inside pipelines.
  --resetlastkey     Reset __last__ key
  -h --help          Output this help and exit
  --version          Output version and exit
"""

import time
import random
import multiprocessing
import csv
# 3rd party imports
from docopt import docopt

def loop(rc, reset_last_key=None):
    """
    Regular debug loop that can be used to test how redis behaves during changes in the cluster.
    """
    if reset_last_key:
        rc.set("__last__", 0)

    last = False
    while last is False:
        try:
            last = rc.get("__last__")
            last = 0 if not last else int(last)
            print("starting at foo{0}".format(last))
        except Exception as e:
            print("error {0}".format(e))
            time.sleep(1)

    for i in range(last, 1000000000):  # noqa
        try:
            print("SET foo{0} {1}".format(i, i))
            rc.set("foo{0}".format(i), i)
            got = rc.get("foo{0}".format(i))
            print("GET foo{0} {1}".format(i, got))
            rc.set("__last__", i)
        except Exception as e:
            print("error {0}".format(e))

        time.sleep(0.05)


def timeit(rc,num,operation,share_lock):
    """
    Time how long it take to run a number of set/get:s
    """
    for i in range(0,num):  # noqa
        key=random.randint(0,10000-1)
        s = "foo{0}".format(key)
        if random.uniform(0,1)>0.5:
            rc.set(s, key)
        else:
            rc.get(s)
        share_lock.acquire()
        operation.value+=1
        share_lock.release()
        

def timeit_pipeline(rc, num,operation,share_lock):
    """
    Time how long it takes to run a number of set/get:s inside a cluster pipeline
    """
    for i in range(0, num):  # noqa
        key=random.randint(0,10000-1)
        s = "foo{0}".format(key)
        p = rc.pipeline()
        if random.uniform(0,1)>0.5:
            p.set(s, i)
        else: 
            p.get(s)
        p.execute()
        share_lock.acquire()
        operation.value+=1
        share_lock.release()
        
 

def monitor(mydict,operation):
    last=0
    existing=0
    flag=0
    while (1):
        time.sleep(1)
        now=operation.value
        if last==now:
            break
        mydict["{0}second".format(existing)]=str((now-last)*2)
        existing=existing+1
        last=now
       
if __name__ == "__main__":
    args = docopt(__doc__, version="0.3.1")
    startup_nodes = [{"host": args['--host'], "port": args['-p']}]
    if not args["--nocluster"]:
        from rediscluster import StrictRedisCluster
        rc = StrictRedisCluster(startup_nodes=startup_nodes, max_connections=32, socket_timeout=0.1, decode_responses=True)
    else:
        from redis import StrictRedis
        rc = StrictRedis(host=args["--host"], port=args["-p"], socket_timeout=0.1, decode_responses=True)
    # create specified number processes
    processes = []
    operation=multiprocessing.Manager().Value('i',0)
    mydict=multiprocessing.Manager().dict()
    share_lock = multiprocessing.Manager().Lock()
    single_request = int(args["-n"]) // int(args["-c"])
    p = multiprocessing.Process(target=monitor,args=(mydict,operation))
    processes.append(p)
    for j in range(int(args["-c"])):
        if args["--timeit"]:
            if args["--pipeline"]:
                p = multiprocessing.Process(target=timeit_pipeline, args=(rc, single_request,operation,share_lock))
            else:
                p = multiprocessing.Process(target=timeit, args=(rc, single_request,operation,share_lock))
        else:
            p = multiprocessing.Process(target=loop, args=(rc, args["--resetlastkey"]))
        processes.append(p)
    t1=time.time()
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    t2 = time.time() - t1
    with open('result.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in mydict.items()]
    print("Tested {0}k operations took: {1} seconds... {2} operations per second".format(int(args["-n"]) / 1000, t2, int(args["-n"]) / t2 * 2))
