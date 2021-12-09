#!/usr/bin/env python3
from requests import Session
from urllib.parse import urljoin
import time

username = 'admin'
password = 'password'

cloud_key_ip = 'controller.mydomain.com'
controller_port = 443
site_name = 'default'

# any device las_seen > 7 days
last_seen_filter = int(time.time()) - 604800

base_url = 'https://{cloud_key_ip}:{controller_port}'.format(cloud_key_ip=cloud_key_ip, controller_port=controller_port)

# How many do you have to forget?
#
#The API call is a **POST** to `/api/s/{site}/cmd/stamgr` with the body `{"macs":["00:1e:35:ff:ff:ff"],"cmd":"forget-sta"}` yes, it does look like you could submit them all in bulk to the API but the webUI doesn't expose that
#
#To fetch the list of all devices in json **GET** `/api/s/{site}/stat/alluser`
#
#Shouldn't be that hard to throw something together in python.

def api_login(sess, base_url):
    payload = {
        'username': username,
        'password': password
    }
    url = urljoin(base_url, '/api/login')
    resp = sess.post(url, json=payload, headers={'Referer': '/login'})
    if resp.status_code == 200:
        print('[*] successfully logged in')
        return True
    else:
        print('[!] failed to login with provided credentials')
        return False

def api_get_clients(sess, base_url, site_name):
    url = urljoin(base_url, '/api/s/{site_name}/stat/alluser'.format(site_name=site_name))
    resp = sess.get(url)
    client_list = resp.json()['data']
    client_list = list(filter(lambda x: x['last_seen'] <= last_seen_filter , client_list ))
    return client_list

def api_del_clients(sess, base_url, site_name, macs):
    payload = {
        'cmd': 'forget-sta',
        'macs': macs
    }
    url = urljoin(base_url, '/api/s/{site_name}/cmd/stamgr'.format(site_name=site_name))
    resp = sess.post(url, json=payload)
    client_list = resp.json()['data']
    return client_list

def client_macs(client_list):
    macs = []
    for client in client_list:
        if 'mac' in client:
            macs.append(client['mac'])
    return macs

if __name__ == '__main__':
    sess = Session()
    sess.verify = False
    
    success = api_login(sess=sess, base_url=base_url)
    if success:
        client_list = api_get_clients(sess=sess, base_url=base_url, site_name=site_name)
        macs = client_macs(client_list=client_list)
        i=0
        api_del_clients(sess=sess, base_url=base_url, site_name=site_name, macs=macs)