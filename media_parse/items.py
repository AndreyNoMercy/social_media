# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaFollowingItem(scrapy.Item):
    _id = scrapy.Field()
    insta_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    is_private = scrapy.Field()
    target = scrapy.Field()

class VkUsersSubscribeItem(scrapy.Item):
    _id = scrapy.Field()
    vk_id = scrapy.Field()
    name = scrapy.Field()
    last_name = scrapy.Field()
    params = scrapy.Field()
    target = scrapy.Field()
