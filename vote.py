#!/usr/local/bin/python2.7
# -*- coding:utf-8 -*- 
'''
@author:     cs
'''
import re, random, sys, os, json, time, datetime, threading, requests, bs4
from random import choice
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
votetime = 0
def count(json_data):
    browser = webdriver.PhantomJS(executable_path=abspath + json_data["executable_path"])
    result = ''
    for p in json_data["counts"]:
        browser.get(p["url"])
        for xpath in p["xpaths"]:
            try:
                element = browser.find_element_by_xpath(xpath["path"])
                result += xpath["format"] % element.text.strip()
            except NoSuchElementException:
                assert 0, "can't find sells"
    browser.close()  
    browser.quit()    
    return result
def get_ip():
    """获取代理IP"""
    url = "http://www.xicidaili.com/nn"
    headers = { "Accept":"text/html,application/xhtml+xml,application/xml;",
                "Accept-Encoding":"gzip, deflate, sdch",
                "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
                "Referer":"http://www.xicidaili.com",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
                }
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    data = soup.table.find_all("td")
    ip_compile = re.compile(r'<td>(\d+\.\d+\.\d+\.\d+)</td>')  # 匹配IP
    port_compile = re.compile(r'<td>(\d+)</td>')  # 匹配端口
    ip = re.findall(ip_compile, str(data))  # 获取所有IP
    port = re.findall(port_compile, str(data))  # 获取所有端口
    return [":".join(i) for i in zip(ip, port)]  # 组合IP+端口，如：115.112.88.23:8080
# 设置 user-agent列表，每次请求时，可在此列表中随机挑选一个user-agnet
uas = [
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0; Baiduspider-ads) Gecko/17.0 Firefox/17.0",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9b4) Gecko/2008030317 Firefox/3.0b4",
    "Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; BIDUBrowser 7.6)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
    ]
def get_url(json_data, savepath, code=0, ips=[]):
    global votetime
    """
                投票
                如果因为代理IP不可用造成投票失败，则会自动换一个代理IP后继续投
    """
    try:
        ip = choice(ips)
    except:
        return False
    else:
        proxies = {
            "http":ip,
        }
        headers2 = { "Accept":"text/html,application/xhtml+xml,application/xml;",
                        "Accept-Encoding":"gzip, deflate, sdch",
                        "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
                        "Referer":"",
                        "User-Agent":choice(uas),
                        }
    try:
        hz_url = json_data["url"] + "&timestrip=" + str(time.time())
        hz_r = requests.get(hz_url, headers=headers2, proxies=proxies)
    except requests.exceptions.ConnectionError:
        if json_data["debug"]:
            print "ConnectionError"
        if not ips:
            print "not ip"
            sys.exit()
        # 删除不可用的代理IP
        if ip in ips:
            ips.remove(ip)
        # 重新请求URL
        get_url(code, ips)
    else:
        date = datetime.datetime.now().strftime('%H:%M:%S')
        status_result = u"失败"
        print hz_r.text
        if hz_r.text == "0":
            votetime += 1
            status_result = u"成功"
        vote_result = u"第%s次 [%s] [%s]：投票%s (剩余可用代理IP数：%s)" % (votetime, date, ip, status_result, len(ips))
        vote_count = u"当前排行:" + count(json_data)
        print vote_result
        print vote_count
        if savefile:
            try:
                f = file(savepath, 'w+')
                f.write(str(vote_result.encode('gbk').strip()) + "\n")
                f.write(str(vote_count.encode('gbk').strip()) + "\n")
            finally:
                f.close()

print u"★★★★★now start vote★★★★★"
abspath = os.path.split(os.path.realpath(__file__))[0] + "/"
with open(abspath + "vote.json", 'r') as js:
    json_data = json.load(js)     
      
ips = []
vote_max = json_data["vote_max"]
times_total = json_data["times_total"]
times_reload = json_data["times_reload"]
time_sleep_random_start = json_data["time_sleep_random_start"]
time_sleep_random_end = json_data["time_sleep_random_end"]
savefile = not json_data["savepath"] == ""
savepath = abspath + time.strftime('%Y-%m-%d', time.localtime(time.time())) + json_data["savepath"]
for i in xrange(1, json_data["times_total"]):
    # 每隔固定次数重新获取一次最新的代理IP，每次可获取最新的100个代理IP
    if votetime >= vote_max:
        print "fullly vote exit"
        break;
    if i % times_reload == 1:
        ips.extend(get_ip())
    t1 = threading.Thread(target=get_url, args=(json_data, savepath, i, ips))
    t1.start()
    time.sleep(random.uniform(time_sleep_random_start, time_sleep_random_end))
print u"★★★★★end vote★★★★★"
