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
    env.server_ip=random.choice(servers_ip)
    # set your own key here
    env.key_filename = ['id_rsa']
    # gateway setting
    # env.gateway = 'root@59.111.148.12'


def test_wrk(port):

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    #server_ip=env.link_end[client_ip]
    server_ip="115.238.122.56"
    run('mkdir $PWD/tmp')
    run('rm -rf $PWD/tmp/{}_{}_wrk.sh'.format(server_ip,port))
    run('rm -rf $PWD/tmp/{}_{}_wrk'.format(server_ip,port))
    run("echo 'wrk -t100 -c400 -d30s http://{}:{} > $PWD/tmp/{}_{}_wrk ' > $PWD/tmp/{}_{}_wrk.sh".format(server_ip,port,server_ip,port,server_ip,port))
    run('echo "sleep 20" >> $PWD/tmp/{}_{}_wrk.sh '.format(server_ip,port))
    run('dtach -n `mktemp -u /root/ss.XXXX` sh  $PWD/tmp/{}_{}_wrk.sh'.format(server_ip,port))

def test_mult_wrk():
    for port in range(8000,8001):
	test_wrk(port)

def cat_mult_wrk():
    for port in range(8000,8001):
	cat_wrk(port)

def cat_wrk(port):

    client_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    #server_ip=env.server_ip
    server_ip="115.238.122.56"
    num=run('cat $PWD/tmp/{}_{}_wrk'.format(server_ip,port))

def stop_client():
    run('rm -rf /root/ss.*')
    run('ps -ef|grep wrk|awk {\'print $2\'}|xargs kill -9')

@parallel
def start():
    execute(set_hosts)

    execute(test_wrk,8000)
    time.sleep(70)
    execute(cat_wrk,8000)


@parallel
def check():
    execute(set_hosts)
    execute(stop_client)
