#!/usr/bin/env python
# encoding: utf-8
import random
import time
from fabric.api import *

# ignore offline hosts
env.skip_bad_hosts = True
env.warn_only = True


# ============================================================
def set_hosts():
    hosts_ip = open('./ip_list/src_list', 'r').readlines()
    env_hosts_list = []
    all_ip = []
    print(hosts_ip)

    # remove \n\r, and add "root@" to the ip
    for ip in hosts_ip:
        ip = ip.strip()
        # check if empty str exist
        if not ip:
            pass
        else:
            new_ip = "root@" + ip
            env_hosts_list.append(new_ip)
            all_ip.append(ip)

    # define fabric hosts and keys
    env.hosts = env_hosts_list
    env.connection_attempts = 5
    env.timeout = 20

    # set your own key here
    env.key_filename = ['id_rsa']
    # gateway setting
    # env.gateway = 'root@59.111.148.12'
    return all_ip

def test_tcp_crr():

    server_ip = open('./ip_list/node_list', 'r').readlines()
    for ip in server_ip:
        ip = ip.strip()
        if not ip:
            pass
        else:
            run('mkdir $PWD/tmp')
            run('rm -rf $PWD/tmp/{}_tcp_crr.sh'.format(ip))
            run('rm -rf $PWD/tmp/{}_crr'.format(ip))
            run("echo 'netperf -t TCP_CRR -H {} -l 20 -- -r 1B,1B -O \" MIN_LAETENCY, MAX_LATENCY, MEAN_LATENCY, P90_LATENCY, P99_LATENCY ,STDDEV_LATENCY ,THROUGHPUT ,THROUGHPUT_UNITS \" > $PWD/tmp/{}_crr ' > $PWD/tmp/{}_tcp_crr.sh".format(ip,ip,ip))
            run('echo "sleep 20" >> $PWD/tmp/{}_tcp_crr.sh '.format(ip))
            run('dtach -n `mktemp -u /root/ss.XXXX` sh  $PWD/tmp/{}_tcp_crr.sh'.format(ip))

def cat_tcp_crr():

    server_ip = open('./ip_list/node_list', 'r').readlines()
    for ip in server_ip:
        ip = ip.strip()
        if not ip:
            pass
        else:
            run('cat $PWD/tmp/{}_crr'.format(ip))

def test_tcp_rr():

    server_ip = open('./ip_list/node_list', 'r').readlines()
    for ip in server_ip:
        ip = ip.strip()
        if not ip:
            pass
        else:
            run('mkdir $PWD/tmp')
            run('rm -rf $PWD/tmp/{}_tcp_rr.sh'.format(ip))
            run('rm -rf $PWD/tmp/{}_rr'.format(ip))
            run("echo 'netperf -t TCP_RR -H {} -l 20 -- -r 1B,1B -O \" MIN_LAETENCY, MAX_LATENCY, MEAN_LATENCY, P90_LATENCY, P99_LATENCY ,STDDEV_LATENCY ,THROUGHPUT ,THROUGHPUT_UNITS \" > $PWD/tmp/{}_rr ' > $PWD/tmp/{}_tcp_rr.sh".format(ip,ip,ip))
            run('echo "sleep 20" >> $PWD/tmp/{}_tcp_rr.sh '.format(ip))
            run('dtach -n `mktemp -u /root/ss.XXXX` sh  $PWD/tmp/{}_tcp_rr.sh'.format(ip))

def cat_tcp_rr():
    server_ip = open('./ip_list/node_list', 'r').readlines()
    link_num=0
    link_server=0
    host=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    for ip in server_ip:
        ip = ip.strip()
        if not ip:
            pass
        else:
            num=run('cat $PWD/tmp/{}_rr|grep Trans/s|awk {{\'print $6\'}}'.format(ip))
            link_num=link_num+float(num)
            link_server+=1
    with open('data/link_num.txt', 'a') as f:
        f.write('{}:{}\n'.format(host,link_num))
    with open('data/link_server.txt', 'a') as f:
        f.write('{}:{}\n'.format(host,link_server))


def caculate_link_num():
    print env.link_num
    print env.link_server
    num=0
    server=0
    for value in env.link_num:
      num+=value
    for value in env.link_server:
      server+=value;

#############################################################
# command line wrapper
#############################################################
@parallel
def start():
    execute(set_hosts)
    #execute(test_tcp_crr)
    #execute(test_tcp_rr)
    #time.sleep(50)
    #execute(cat_tcp_crr)
    execute(cat_tcp_rr)


@parallel
def check():
    execute(set_hosts)
