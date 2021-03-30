# -*- coding: utf-8 -*-
import scrapy
import json
from media_parse.items import VkUsersSubscribeItem


class VkParserSpider(scrapy.Spider):
    name = 'VK_followers_subs'
    allowed_domains = ['api.vk.com']
    base_url = 'https://api.vk.com/method/'
    fields = '[photo_id, verified, sex, bdate, city, country, home_town, has_photo, photo_max_orig,' \
             ' has_mobile, contacts, site, education, universities, schools, status, last_seen, ' \
             'followers_count, occupation, nickname, relatives, relation, personal, ' \
             'connections, exports, activities, interests, music, movies, tv, books, games, about, ' \
             'quotes, timezone, maiden_name, career, military]'

    def __init__(self, name_for_parse: str, method: str, method_2: str, access_token: str, **kwargs):
        self.__name_for_parse = name_for_parse
        self.__access_token = access_token
        self.__method = method
        self.__method_2 = method_2
        self.counter = 1
        self.start_urls = [f'{self.base_url}{self.__method}?group_id={self.__name_for_parse}&access_token'
                           f'={self.__access_token}&v=5.110']
        super().__init__(**kwargs)

    def parse(self, response):
        tmp_dict = json.loads(response.text)
        parsing_list = tmp_dict['response']['items']
        if tmp_dict['response']['count'] % len(parsing_list):
            paginator = (tmp_dict['response']['count'] // len(parsing_list)) + 1
        else:
            paginator = tmp_dict['response']['count'] // len(parsing_list)
        for id in parsing_list:
            url = f'{self.base_url}users.get?user_ids={id}&fields={self.fields}&access_token={self.__access_token}&v=5.110'
            yield response.follow(url, callback=self.parse_user)
        while self.counter != paginator:
            url = f'{self.base_url}{self.__method}?group_id={self.__name_for_parse}&offset=' \
                  f'{self.counter * len(parsing_list)}&access_token={self.__access_token}&v=5.110'
            yield response.follow(url, callback=self.get_parsing_list)
            self.counter += 1

    def get_parsing_list(self, response):
        tmp_dict = json.loads(response.text)
        parsing_list = tmp_dict['response']['items']
        for id in parsing_list:
            url = f'{self.base_url}users.get?user_ids={id}&fields={self.fields}&access_token={self.__access_token}&v=5.110'
            yield response.follow(url, callback=self.parse_user)

    def parse_user(self, response):
        user_dict = json.loads(response.text)['response'][0]
        try:
            if user_dict['is_closed']:
                item = VkUsersSubscribeItem(
                    vk_id=user_dict.pop('id'),
                    name=user_dict.pop('first_name'),
                    last_name=user_dict.pop('last_name'),
                    params=user_dict,
                    target=None
                )
                yield item
            else:
                url = f'{self.base_url}{self.__method_2}?user_id={user_dict["id"]}' \
                      f'&&access_token={self.__access_token}&v=5.110'
                yield response.follow(url, callback=self.parse_user_target, cb_kwargs=user_dict)
        except:
            item = VkUsersSubscribeItem(
                vk_id=user_dict.pop('id'),
                name=user_dict.pop('first_name'),
                last_name=user_dict.pop('last_name'),
                params=user_dict,
                target=None
            )
            yield item

    def parse_user_target(self, response, **kwargs):
        item = VkUsersSubscribeItem(
            vk_id=kwargs.pop('id'),
            name=kwargs.pop('first_name'),
            last_name=kwargs.pop('last_name'),
            params=kwargs,
            target=json.loads(response.text)['response'],
        )
        yield item

