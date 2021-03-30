from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from media_parse import settings
from media_parse.spiders.VK_parser import VkParserSpider
group_name = ''
method = 'groups.getMembers'
method_2 = 'users.getSubscriptions'
access_token = ''

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_procc = CrawlerProcess(settings=crawl_settings)
    crawl_procc.crawl(VkParserSpider, group_name, method, method_2, access_token)
    crawl_procc.start()
