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

def set_client():
    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    server_ip=env.link_end[client_ip]
    #run('rm -rf /root/ss.*')
    #run('dtach -n `mktemp -u /root/ss.XXXX` iperf  -c 115.238.122.51  -P 6000 -p 5001 -t 200')
    run('dtach -n `mktemp -u /root/ss.XXXX` iperf  -c {}  -P 3000 -p 5001 -t 200s'.format(server_ip))
    #run('ps -ef|grep wrk|awk {{\'print $2\'}}|xargs kill -9')
    #run('dtach -n `mktemp -u /root/ss.XXXX` ./wrk -t100 -c400 -d300s http://115.238.122.60:8000')

def stop_client():
    run('rm -rf /root/ss.*')
    run('ps -ef|grep iperf|awk {\'print $2\'}|xargs kill -9')
#############################################################
# command line wrapper
#############################################################
@parallel
def start():
    execute(set_hosts)
    execute(set_client)


@parallel
def check():
    execute(set_hosts)
    execute(stop_client)
