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


def timeit(rc,num):
    """
    Time how long it take to run a number of set/get:s
    """
    for i in range(0,num):  # noqa
        key=random.randint(0,1000000-1)
        s = "foo{0}".format(key)
        if random.uniform(0,1)>0.05:
            rc.set(s, key)
        else:
            rc.get(s)       

def timeit_tput(rc,num,tput):
    """
    Time how long it take to run a number of set/get:s
    """
    start=time.time()
    existing=0
    operation=0
    last=0
    for i in range(0,num):  # noqa
        key=random.randint(0,1000000-1)
        s = "foo{0}".format(key)
        if random.uniform(0,1)>0.5:
            rc.set(s, key)
        else:
            rc.get(s)
        operation+=1
        if time.time()>=start+existing+1:
            tput[existing]=operation-last
            existing+=1
            last=operation
    tput[existing]=operation-last
    
def timeit_pipeline_tput(rc, num,tput):
    """
    Time how long it takes to run a number of set/get:s inside a cluster pipeline
    """
    start=time.time()
    existing=0
    operation=0
    last=0
    for i in range(0, num):  # noqa
        key=random.randint(0,10000-1)
        s = "foo{0}".format(key)
        p = rc.pipeline()
        if random.uniform(0,1)>0.5:
            p.set(s, i)
        else:
            p.get(s)
        p.execute()
        operation+=1
        if time.time()>=start+existing+1:
            tput[existing]=operation-last
            existing+=1
            last=operation
    tput[existing]=operation-last



def timeit_pipeline(rc, num):
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
    manager = multiprocessing.Manager()
    tput = manager.dict()
    single_request = int(args["-n"]) // int(args["-c"])
    for j in range(int(args["-c"])-1):
        if args["--pipeline"]:
            p = multiprocessing.Process(target=timeit_pipeline, args=(rc, single_request))
        else:
            p = multiprocessing.Process(target=timeit, args=(rc, single_request))
        processes.append(p)
    if args["--pipeline"]:
        p = multiprocessing.Process(target=timeit_pipeline_tput, args=(rc, single_request,tput))
    else:
        p = multiprocessing.Process(target=timeit_tput, args=(rc, single_request,tput))
    processes.append(p)
    t1=time.time()
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    t2 = time.time() - t1
    for value in tput.values():
        print(value*int(args["-c"])*2)
    print("Tested {0}k operations took: {1} seconds... {2} operations per second".format(int(args["-n"]) / 1000, t2, int(args["-n"]) / t2 * 2))
