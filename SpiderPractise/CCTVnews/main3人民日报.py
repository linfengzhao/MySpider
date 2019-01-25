# -*- coding: utf-8 -*-
# 爬取人民日报的新闻早班车
import csv
import datetime
import re
import time
from urllib.parse import urlencode
import json

import requests
from pyquery import PyQuery as pq

from SpiderPractise.CCTVnews.utils import get_user_agent, EARLY_SECTIONS


def sogou_weixin(keyword='人民日报'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'weixin.sogou.com',
        'Referer': 'https://weixin.sogou.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_user_agent()
    }
    params = {
        'type': '2',
        's_from': 'input',
        'query': keyword,
        'ie': 'utf8',
        '_sug_': 'n',
        '_sug_type_': ''
    }
    base_url = 'https://weixin.sogou.com/weixin?'
    try:
        url = base_url + urlencode(params)
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            print("Get Successfully!", url)
            doc = pq(response.text)
            media_link = doc('.gzh-name a').attr('href')
            print(media_link)
            return media_link
        else:
            print("Get Failed", url)
            return None
    except Exception as e:
        print("ERROR", e.args)
        return None


def media_links(keyword='来了！新闻早班车'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'weixin.sogou.com',
        'Referer': 'https://weixin.sogou.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_user_agent()
    }
    params = {
        'type': '2',
        's_from': 'input',
        'query': keyword,
        'ie': 'utf8',
        '_sug_': 'n',
        '_sug_type_': ''
    }
    base_url = 'https://weixin.sogou.com/weixin?'
    try:
        url = base_url + urlencode(params)
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            print("Get Successfully!", url)
            doc = pq(response.text)
            links = list()
            link = dict()
            lis = doc('.news-list li').items()
            for li in lis:
                link['content_url'] = li('.img-box a').attr('href')
                link['datetime'] = time.strftime('%Y.%m.%d', time.localtime(int(li('.txt-box .s-p').attr('t'))))
                link['title'] = '来了！新闻早班车'
                print(link)
                links.append(link.copy())
            return links
        else:
            print("Get Failed", url)
            return None
    except Exception as e:
        print("ERROR", e.args)
        return None


def early_news_link(link):
    if link is None:
        return None
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'mp.weixin.qq.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_user_agent()
    }
    try:
        response = requests.get(link, headers=headers, timeout=30)
        if response.status_code == 200:
            print("Get Successfully!", link)
            if response.encoding == 'ISO-8859-1':
                text = response.text.encode('ISO-8859-1').decode('utf-8')
            else:
                text = response.text
            early_pattern = re.compile('var msgList = (.*?);\n', re.S)
            msg_lists = json.loads(re.search(early_pattern, text).group(1))
            for msg in msg_lists.get('list'):
                if msg.get('app_msg_ext_info').get('title') == '来了！新闻早班车':
                    result = {
                        'title': msg.get('app_msg_ext_info').get('title'),
                        'datetime': time.strftime('%Y.%m.%d', time.localtime(msg.get('comm_msg_info').get('datetime'))),
                        'content_url': 'https://mp.weixin.qq.com' + msg.get('app_msg_ext_info').get('content_url').replace('&amp;', '&')
                    }
                    print(result)
                    return result
        else:
            print("Get Failed", link)
            return None
    except Exception as e:
        print("ERROR", e.args)
        return None


def early_news_page(early_news):
    if early_news is None:
        return None
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'mp.weixin.qq.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_user_agent()
    }
    if early_news:
        # try:
        url = early_news.get('content_url')
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            articles = process_page(response.text)
            save_early_new(early_news, articles)
        else:
            print("Get Failed", url)
        # except Exception as e:
        #     print("Get Failed! ERROR:", e.args)
    pass


def process_page(content):
    doc = pq(content)
    article_list = list()
    process_result = {
        'layer': 'flashNewsLayer',
        'content1': '',
        'flashnews_image': 'no',
        'discard': 'no',
        'region': '',
        'latitude': '',
        'longitude': '',
        'detail_url': '',
        'flashnews_video': '',
        'section': '',
        'time': re.search('.*?var publish_time = "(.*?)" || "";', content, re.S).group(1).replace('-', '.')
    }
    if doc('#js_content > section:first-of-type').attr('data-tools'):
        doc('#js_content > section:first-of-type').remove()
    sections = doc('#js_content > section').items()
    count = 0
    print(doc('#js_content > section'))
    for section in sections:
        text = section.text()
        if text == '生活提示':
            break
        # if count % 2 == 0:
        elif text in ['要闻', '社会', '政策']:
            process_result['section'] = text

        else:

            items = section.children().items()
            for i in items:
                text2 = i.text()
                if text2 == '':
                    continue
                process_result['content1'] = text2
                process_result['flashnews_image'] = i('img').attr('data-src')
                if process_result['flashnews_image'] is None:
                    process_result['flashnews_image'] = 'no'
                print(process_result)
                article_list.append(process_result.copy())
                process_result['content1'] = ''
                process_result['flashnews_image'] = 'no'
        # count += 1
    return article_list


def save_early_new(early_news, articles):
    filename = early_news.get('title') + early_news.get('datetime') + '.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:  # newline表示行与行之间
        fieldnames = ['layer', 'content1', 'flashnews_image', 'discard', 'region', 'latitude', 'longitude',
                      'detail_url', 'flashnews_video', 'section', 'time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)


def main():
    link = sogou_weixin()
    early_news = early_news_link(link)
    early_news_page(early_news)


if __name__ == '__main__':
    main()
    # medias = media_links()
    # for media in medias:
    #     print(media)
    #     early_news_page(media)
    #     time.sleep(10)
