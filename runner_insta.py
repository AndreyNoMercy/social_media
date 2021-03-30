from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from media_parse import settings_insta
from media_parse.spiders.insta_followers import InstaFollowersSpider

login = ''
password = ''
users = ['']

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings_insta)
    crawl_procc = CrawlerProcess(settings=crawl_settings)
    crawl_procc.crawl(InstaFollowersSpider, users, login, password)
    crawl_procc.start()
