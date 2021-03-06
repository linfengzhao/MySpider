# -*- coding: utf-8 -*-
import sys
import os.path
# 添加项目路径，保证UseScrapy文件夹能查询到，避免出现ModuleNotFoundError
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_directory, "../..")))

from scrapy.utils.project import get_project_settings
from UseScrapy.scrapyuniversal.scrapyuniversal.utils import get_config
from UseScrapy.scrapyuniversal.scrapyuniversal.spiders.universal import UniversalSpider
from scrapy.crawler import CrawlerProcess


def run():
    name = sys.argv[1]
    custom_settings = get_config(name)
    # 爬取使用的Spider名称
    spider = custom_settings.get('spider')
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    # 合并设置
    settings.update(custom_settings.get('settings'))
    process = CrawlerProcess(settings)
    # 启动爬虫
    process.crawl(spider, **{'name': name})
    process.start()


if __name__ == '__main__':
    run()
