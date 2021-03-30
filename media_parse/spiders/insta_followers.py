# -*- coding: utf-8 -*-
from copy import deepcopy
import re
import json
import scrapy
from urllib.parse import urlencode
from media_parse.items import InstaFollowingItem


class InstaFollowersSpider(scrapy.Spider):
    name = 'inst_followers_following'
    allowed_domains = ['instagram.com', 'www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']
    graphtql_url = 'https://www.instagram.com/graphql/query/?query_hash='
    query_hash = {
        'followers': 'c76146de99bb02f6415203be841dd25a',
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
        'posts': '',
        'post_detail': '',
    }
    variables = {
        'id': '',
        'include_reel': True,
        'fetch_mutual': False,
        'first': 100,
    }
    def __init__(self, users, login: str, passwd: str, **kwargs):
        self.__login = login
        self.__password = passwd
        self.__users = users
        self.counter = 0
        super().__init__(**kwargs)

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_url,
            method='POST',
            callback=self.main_login_parse,
            formdata={'username': self.__login,
                      'enc_password': self.__password},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_login_parse(self, response):
        resp_data = json.loads(response.text)
        if resp_data['authenticated']:
            for user in self.__users:
                self.counter += 1
                yield response.follow(
                    f'{self.start_urls[0]}{user}/', callback=self.parse_user, cb_kwargs={'user': user})
        else:
            print(resp_data)

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, user):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % user, text
        ).group()
        return json.loads(matched).get('id')

    def parse_user(self, response, user):
        variables = deepcopy(self.variables)
        variables['id'] = self.fetch_user_id(response.text, user)
        followers_url = self.make_grapthql_url(self.query_hash['followers'], variables)
        self.counter += 1
        yield response.follow(followers_url, callback=self.parse_followers,
                              cb_kwargs={'user': user, 'variables': variables})

    def parse_followers(self, response, user, variables):
        data = json.loads(response.text)
        for follower in data.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('edges', []):
            if follower.get('node'):
                follower_dict = follower.get('node')
                follower_dict['target'] = []
                if follower_dict.get('is_private'):
                    item = InstaFollowingItem(
                        insta_id=follower_dict.pop('id'),
                        username=follower_dict.pop('username'),
                        full_name=follower_dict.pop('full_name'),
                        profile_pic_url=follower_dict.pop('profile_pic_url'),
                        is_private=follower_dict.pop('is_private'),
                        target=follower_dict.pop('target'),
                    )
                    yield item
                else:
                    following_variables = deepcopy(self.variables)
                    following_variables['id'] = follower_dict.get('id')
                    self.counter += 1
                    yield response.follow(self.make_grapthql_url(self.query_hash['following'], following_variables),
                                          callback=self.parse_following,
                                          cb_kwargs={'follower_dict': follower_dict,
                                                     'following_variables': following_variables})
        if data.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('page_info', {}).get('has_next_page'):
            after = data.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('page_info', {}).get('end'
                                                                                                              '_cursor')
            variables['after'] = after
            self.counter += 1
            yield response.follow(self.make_grapthql_url(self.query_hash['followers'], variables),
                                  callback=self.parse_followers,  cb_kwargs={'user': user, 'variables': variables})

    def parse_following(self, response, follower_dict, following_variables):
        data = json.loads(response.text)
        for follow in data.get('data', {}).get('user', {}).get('edge_follow', {}).get('edges', []):
            if follow.get('node'):
                follower_dict['target'].extend([follow.get('node')])
        if data.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {}).get('has_next_page'):
            after = data.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {}).get('end_cursor')
            following_variables['after'] = after
            self.counter += 1
            yield response.follow(self.make_grapthql_url(self.query_hash['following'], following_variables),
                                  callback=self.parse_following, cb_kwargs={'follower_dict': follower_dict,
                                                                            'following_variables': following_variables})
        else:
            item = InstaFollowingItem(
                insta_id=follower_dict.pop('id'),
                username=follower_dict.pop('username'),
                full_name=follower_dict.pop('full_name'),
                profile_pic_url=follower_dict.pop('profile_pic_url'),
                is_private=follower_dict.pop('is_private'),
                target=follower_dict.pop('target'),
            )
            yield item

    def make_grapthql_url(self, query_hash, user_vars):
        return f'{self.graphtql_url}{query_hash}&{urlencode(user_vars)}'
