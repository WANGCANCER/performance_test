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
    srcs_ip=[]
    dests_ip=[]
    for line in open('./ip_list/client_list', 'r').readlines():
         clients_ip.append("root@"+line.strip('\n'))
         srcs_ip.append(line.strip('\n'))

    for line in open('./ip_list/server_list', 'r').readlines():
         servers_ip.append("root@"+line.strip('\n'))

    for line in open('./ip_list/dest_list', 'r').readlines():
         dests_ip.append(line.strip('\n'))

    env.link_end=dict(zip(srcs_ip,dests_ip))

    env.roledefs={'server':servers_ip,'client':clients_ip}
    env.connection_attempts = 5
    env.timeout = 20

    env.key_filename = ['id_rsa']

@roles('server')
def set_server():

    server_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    run('sh set_max_open_file.sh')
    run('cd c1000k-master/ && make')
    run('sh set_max_open_file.sh && dtach -n `mktemp -u /root/ss.XXXX` ./c1000k-master/server 8000')

@roles('server')
def cat_link():

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    run('cd c1000k-master/ && tail -n 5 c1000k_log')

@roles('client')
def set_client():

    src_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    dest_ip=env.link_end[src_ip]
    run('sh set_max_open_file.sh')
    run('cd c1000k-master/ && make')
    run('echo "" > c1000k-master/c1000k_log ')
    #run('dtach -n `mktemp -u /root/ss.XXXX` ./c1000k-master/client {} 8000'.format(dest_ip),pty=False)
    run('sh set_max_open_file.sh && ./c1000k-master/client {} 8000'.format(dest_ip))

#############################################################
# command line wrapper
#############################################################
@parallel
def start():
    execute(set_hosts)
    execute(set_server)
    #time.sleep(5)
    execute(set_client)
    execute(cat_link)


@parallel
def check():
    execute(set_hosts)
