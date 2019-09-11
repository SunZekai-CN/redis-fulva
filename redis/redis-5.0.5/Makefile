# Top level makefile, the real shit is at src/Makefile

default: all

.DEFAULT:
	cd src && $(MAKE) $@

install:
	cd src && $(MAKE) $@

.PHONY: install

cluster_clean:
	rm -rf ../redis-cluster/7001/appendonly.aof ../redis-cluster/7001/dump.rdb ../redis-cluster/7001/nodes-7001.conf
	rm -rf ../redis-cluster/7002/appendonly.aof ../redis-cluster/7002/dump.rdb ../redis-cluster/7002/nodes-7002.conf
	rm -rf ../redis-cluster/7003/appendonly.aof ../redis-cluster/7003/dump.rdb ../redis-cluster/7003/nodes-7003.conf
	rm -rf ../redis-cluster/7004/appendonly.aof ../redis-cluster/7004/dump.rdb ../redis-cluster/7004/nodes-7004.conf
	rm -rf ../redis-cluster/7005/appendonly.aof ../redis-cluster/7005/dump.rdb ../redis-cluster/7005/nodes-7005.conf
	rm -rf ../redis-cluster/7006/appendonly.aof ../redis-cluster/7006/dump.rdb ../redis-cluster/7006/nodes-7006.conf
cluster_create:
	./src/redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 --cluster-replicas 1

cluster_start:
	./src/redis-server ../redis-cluster/7001/redis.conf
	./src/redis-server ../redis-cluster/7002/redis.conf
	./src/redis-server ../redis-cluster/7003/redis.conf
	./src/redis-server ../redis-cluster/7004/redis.conf
	./src/redis-server ../redis-cluster/7005/redis.conf
	./src/redis-server ../redis-cluster/7006/redis.conf
