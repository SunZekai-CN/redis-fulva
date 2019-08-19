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

# 3rd party imports
from docopt import docopt

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
    for i in range(0, int(args["-n"])):  # noqa
        s = "foo{0}".format(i)
        rc.set(s, i)
