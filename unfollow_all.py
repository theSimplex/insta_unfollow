#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import requests
import json

instagram_url = 'https://www.instagram.com'
login_route = '%s/accounts/login/ajax/' % (instagram_url)
logout_route = '%s/accounts/logout/' % (instagram_url)
profile_route = '%s/%s/?__a=1'
query_route = '%s/graphql/query/' % (instagram_url)
unfollow_route = '%s/web/friendships/%s/unfollow/'

session = requests.Session()

def login():
    session.headers.update({
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'),
        'X-Instagram-AJAX': '1',
        'X-Requested-With': 'XMLHttpRequest'
    })
    session.cookies.update({
        'ig_pr': '1',
        'ig_vw': '1920',
    })

    reponse = session.get(instagram_url)
    session.headers.update({
        'X-CSRFToken': reponse.cookies['csrftoken']
    })

    time.sleep(random.randint(2, 6))

    post_data = {
        'username': os.environ.get('USERNAME'),
        'password': os.environ.get('PASSWORD')
    }

    reponse = session.post(login_route, data=post_data, allow_redirects=True)
    reponse_data = json.loads(reponse.text)

    if reponse_data['authenticated']:
        session.headers.update({
            'X-CSRFToken': reponse.cookies['csrftoken']
        })
    print(reponse_data)
    return reponse_data['authenticated']

def unfollow(user):
    print('Unfollowing {}'.format(user['full_name']))
    response = session.post(unfollow_route % (instagram_url, user['id']))
    response = json.loads(response.text)

    if response['status'] != 'ok':
        print('ERROR: {}'.format(unfollow.text))
        time.sleep(18000)
    else:
        print('Done')

def logout():
    post_data = {
        'csrfmiddlewaretoken': session.cookies['csrftoken']
    }

    logout = session.post(logout_route, data=post_data)

    if logout.status_code == 200:
        return True
    return False

# Not so useful, it's just to simulate human actions better
def get_user_profile(username):
    response = session.get(profile_route % (instagram_url, username))
    try:
        response = json.loads(response.text)
        return response['graphql']['user']
    except:
        print(response.text)
        return False



def get_first_page_follows():
    follows_list = []

    follows_post = {
        'query_id': 17874545323001329,
        'variables': {
            'id': session.cookies['ds_user_id'],
            'first': 20
        }
    }
    follows_post['variables'] = json.dumps(follows_post['variables'])
    session.headers.update({'Content-Type': 'application/json'})
    response = session.post(query_route, data=json.dumps(follows_post))
    response = json.loads(response.text)

    for edge in response['data']['user']['edge_follow']['edges']:
        follows_list.append(edge['node'])
    return follows_list

def main(unfollow_all=True):
    if not os.environ.get('USERNAME') or not os.environ.get('PASSWORD'):
        sys.exit('please provide USERNAME and PASSWORD environement variables. Abording...')
    while True:
        if not login():
            sys.exit('login failed, verify user/password combination')

        print('You\'re now logged as {}'.format(os.environ.get('USERNAME')))

        # time.sleep(random.randint(1, 3))

        # if not get_user_profile(os.environ.get('USERNAME')):
        #     time.sleep(1800)
        #     continue

        time.sleep(random.randint(2, 6))

        follows_list = get_first_page_follows()

        if len(follows_list) > 0:
            print('Begin to unfollow {} users...'.format(len(follows_list)))

            for user in follows_list:
                print('unfollowing {}'.format(user['username']))
                unfollow(user)
                time.sleep(random.randint(5, 10) * len(follows_list))
        else:
            is_logged_out = logout()
            if is_logged_out:
                sys.exit(0)
        logout()
        time.sleep(random.randint(600, 3600))

if __name__ == "__main__":
    main() 