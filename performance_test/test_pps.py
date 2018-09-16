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
    run('ps -ef|grep sar|awk {{\'print $2\'}}|xargs kill -9')
    run('mkdir tmp')
    run("echo 'sar -n DEV 2 > $PWD/tmp/{}'> $PWD/tmp/{}_sar.sh".format(server_ip,server_ip))
    run('dtach -n `mktemp -u /root/ss.XXXX` sh $PWD/tmp/{}_sar.sh '.format(server_ip))

@roles('server')
def cat_pps():

    server_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    run('ps -ef|grep sar|awk {{\'print $2\'}}|xargs kill -9')
    run('rm -rf ss.*')
    run('cat $PWD/tmp/{}|grep -a eth0|awk {{\'print $4\'}}| sort -n|tail'.format(server_ip))

@roles('client')
def set_client():

    src_ip=run('echo "{}"|awk -F "@"  {{\'print $2\'}}'.format(env.host_string))
    dest_ip=env.link_end[src_ip]
    #run('dtach -n `mktemp -u /root/ss.XXXX` ./c1000k-master/client {} 8000'.format(dest_ip),pty=False)
    run('dtach -n `mktemp -u /root/ss.XXXX` sh pktgen.sh {}'.format(dest_ip))

#############################################################
# command line wrapper
#############################################################
@parallel
def test():
    execute(set_hosts)
    execute(set_server)
    time.sleep(5)
    execute(set_client)

@parallel
def cat():
    execute(set_hosts)
    execute(cat_pps)

@parallel
def check():
    execute(set_hosts)
