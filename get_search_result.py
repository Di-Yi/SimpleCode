#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Yi
# Datetime: 2019/11/14 12:58

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, errors

# 配置pymongo
mongo_client = MongoClient('localhost', 27017)
spider = mongo_client['weibo']
profile = spider['search']

url = "https://s.weibo.com/weibo"

h = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7
Connection: keep-alive
Cookie: _s_tentry=passport.weibo.com; Apache=1629906121789.0754.1560254701366; SINAGLOBAL=1629906121789.0754.1560254701366; ULV=1560254701536:1:1:1:1629906121789.0754.1560254701366:; login_sid_t=d4bedca81da1af6540abaee6116048cd; cross_origin_proto=SSL; UM_distinctid=16db589687027b-04af53aadd985c-1d3b6b54-13c680-16db5896871b2; secsys_id=70dc1c3c6e9befd93360b15c379d9a01; UOR=,,www.baidu.com; SSOLoginState=1581252986; SCF=ApeOZib8nXL6GsFq0ztp6qCvrKHeBZHMyp8vcqH8NpFqp67lXpI9REkkz7cabAFs4HjkwLaJa0nmKytrVwe-eRA.; SUB=_2A25zT5fzDeRhGeFO41oW8ivIwjSIHXVQPI47rDV8PUNbmtAfLWr_kW9NQVHtbp8WYRs9KnQKhxVjp6B6lTp-0pqY; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh1v3nUAV47FyBMIbwDYJ025JpX5KzhUgL.FoM71hnNeo-X1Kn2dJLoI7U3UN.peh5E; SUHB=0U1ZEDVkMHC7PA; ALF=1613568802; wvr=6; webim_unReadCount=%7B%22time%22%3A1582032902697%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D; WBStorage=42212210b087ca50|undefined
Host: s.weibo.com
Referer: https://s.weibo.com/weibo/%25E7%258C%25AA%25E7%2598%259F?topnav=1&wvr=6&b=1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"""


def handle_header(s):
    dic = {}
    li = s.split('\n')
    for l in li:
        dic[l.split(': ')[0]] = l.split(': ')[1]

    return dic


def handle(page, year, month, day, hour):
    if hour == 23:
        load = {
            'q': '郭涛道歉',
            'typeall': '1',
            'suball': '1',
            'timescope': f'custom:{year}-{month}-{day}-{hour}:{year}-{month}-{int(day) + 1}-0',
            'Refer': 'g',
            'page': page
        }
    else:
        load = {
            'q': '郭涛道歉',
            'typeall': '1',
            'suball': '1',
            'timescope': f'custom:{year}-{month}-{day}-{hour}:{year}-{month}-{day}-{hour + 1}',
            'Refer': 'g',
            'page': page
        }

    j = requests.get(url, headers=handle_header(h), params=load, timeout=(10, 10))
    return j.text


def filter_info(content, _date, _mid):
    """
    过滤无效信息
    :param content:
    :param _date:
    :param _mid:
    :return:
    """
    _content = content.find('div', {'class': 'content'})
    nick_name = _content.find('p')['nick-name']
    blog = _content.find_all('p', {'class': 'txt'})[-1].text.replace('<em class="s-color-red">郭涛道歉</em>',
                                                                     '郭涛道歉').strip().replace('\n', '\\n')
    create = _content.find_all('p', {'class': 'from'})[-1].a.text.strip().replace('\n', '\\n')
    date_str = "".join(_date)

    data = {'mid': _mid, 'nick_name': nick_name, 'create': create, 'blog': blog, 'date_str': date_str}

    try:
        profile.update_one(data, {'$set': data}, upsert=True)
    except errors.DuplicateKeyError as e:
        print(e)
        return False

    return True


if __name__ == '__main__':
    """
    时间
    2018年 8.6 / 9.3 / 10.1 / 10.29 / 11.26 / 12.24
    2019年 1.21 / 2.18 / 3.18 / 4.15 / 5.13 / 6.10 / 7.8 / 8.5 / 9.2 / 9.30 / 10.28 / 11.25 / 12.23
    2020年 1.20
    """
    date_list = [
        ['2018', '08', '06'],
        ['2018', '09', '03'],
        ['2018', '10', '01'],
        ['2018', '10', '29'],
        ['2018', '11', '26'],
        ['2018', '12', '24'],
        ['2019', '01', '21'],
        ['2019', '02', '18'],
        ['2019', '03', '18'],
        ['2019', '04', '15'],
        ['2019', '05', '13'],
        ['2019', '06', '10'],
        ['2019', '07', '08'],
        ['2019', '08', '05'],
        ['2019', '09', '02'],
        ['2019', '09', '30'],
        ['2019', '10', '28'],
        ['2019', '11', '25'],
        ['2019', '12', '23'],
        ['2020', '01', '20'],
    ]
    mid_total = []

    for date in date_list[1:]:
        for dayHour in range(0, 24):
            sign = True
            print(f"{date}" + " " + str(dayHour))
            for p in range(1, 51):
                print(p)
                soup = BeautifulSoup(handle(p, date[0], date[1], date[2], dayHour), 'lxml')
                contents = soup.find_all('div', {'class': 'card-wrap'})
                if not sign:
                    break
                for c in contents:
                    try:
                        mid = c['mid']
                        if mid in mid_total:
                            sign = False
                            break
                        mid_total.append(mid)
                        filter_info(c, date, mid)
                    except KeyError as e:
                        pass
