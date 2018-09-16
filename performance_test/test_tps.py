#!/usr/bin/env python
# encoding: utf-8
import random
import time
from fabric.api import *

# ignore offline hosts
env.skip_bad_hosts = True
env.warn_only = True
sizes=['1B,1B','512B,32kB','512B,1mB','1mB,512B']

# ============================================================
def set_hosts():
    clients_ip=[]
    servers_ip=[]
    for line in open('./ip_list/client_list', 'r').readlines():
          clients_ip.append(line.strip('\n'))

    for line in open('./ip_list/server_list', 'r').readlines():
          servers_ip.append(line.strip('\n'))

    env.link_end=dict(zip(clients_ip,servers_ip))
    env_hosts_list = []

    # remove \n\r, and add "root@" to the ip
    for client_ip in clients_ip:

        client_ip = client_ip.strip()
        if not client_ip:
            pass
        else:
            new_ip = "root@" + client_ip
            env_hosts_list.append(new_ip)

    # define fabric hosts and keys
    env.hosts = env_hosts_list
    env.connection_attempts = 5
    env.timeout = 20

    # set your own key here
    env.key_filename = ['id_rsa']
    # gateway setting
    # env.gateway = 'root@59.111.148.12'


def test_tcp_rr(size):

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    server_ip=env.link_end[client_ip]
    run('mkdir $PWD/tmp')
    run('rm -rf $PWD/tmp/{}_tcp_rr.sh'.format(server_ip))
    run('rm -rf $PWD/tmp/{}_rr'.format(server_ip))
    run('ps -ef|grep netperf|awk {{print "$2"}}|xargs kill -9')
    run("echo 'netperf -t TCP_RR -H {} -l 20 -- -r {} -O \" MIN_LAETENCY, MAX_LATENCY, MEAN_LATENCY, P90_LATENCY, P99_LATENCY ,STDDEV_LATENCY ,THROUGHPUT ,THROUGHPUT_UNITS \" > $PWD/tmp/{}_rr ' > $PWD/tmp/{}_tcp_rr.sh".format(server_ip,size,server_ip,server_ip))
    run('echo "sleep 20" >> $PWD/tmp/{}_tcp_rr.sh '.format(server_ip))
    run('dtach -n `mktemp -u /root/ss.XXXX` sh  $PWD/tmp/{}_tcp_rr.sh'.format(server_ip))

def cat_tcp_rr():

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    server_ip=env.link_end[client_ip]
    num=run('cat $PWD/tmp/{}_rr|grep Trans/s |awk -F "Trans/s" {{\'print $1\'}}'.format(server_ip))
    with open('data/num.txt', 'a') as f:
        f.write('{}\n'.format(num.strip()))
def test_tcp_crr(size):

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    server_ip=env.link_end[client_ip]
    run('mkdir $PWD/tmp')
    run('rm -rf $PWD/tmp/{}_tcp_crr.sh'.format(server_ip))
    run('rm -rf $PWD/tmp/{}_crr'.format(server_ip))
    run('ps -ef|grep netperf|awk {{print "$2"}}|xargs kill -9')
    run("echo 'netperf -t TCP_CRR -H {} -l 20 -- -r {} -O \" MIN_LAETENCY, MAX_LATENCY, MEAN_LATENCY, P90_LATENCY, P99_LATENCY ,STDDEV_LATENCY ,THROUGHPUT ,THROUGHPUT_UNITS \" > $PWD/tmp/{}_crr ' > $PWD/tmp/{}_tcp_crr.sh".format(server_ip,size,server_ip,server_ip))
    run('echo "sleep 20" >> $PWD/tmp/{}_tcp_crr.sh '.format(server_ip))
    run('dtach -n `mktemp -u /root/ss.XXXX` sh  $PWD/tmp/{}_tcp_crr.sh'.format(server_ip))

def cat_tcp_crr():

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    server_ip=env.link_end[client_ip]
    num=run('cat $PWD/tmp/{}_crr|grep Trans/s |awk -F "Trans/s" {{\'print $1\'}}'.format(server_ip))
    with open('data/num.txt', 'a') as f:
        f.write('{}\n'.format(num.strip()))
#############################################################
# command line wrapper
#############################################################
@parallel
def start():
    execute(set_hosts)
    for size in sizes:

      execute(test_tcp_rr,size)
      time.sleep(50)
      execute(cat_tcp_rr)


@parallel
def check():
    execute(set_hosts)
