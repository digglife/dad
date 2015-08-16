#!/usr/bin/env python
# -*- coding:utf8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import os
import sys

#album = "http://www.douban.com/photos/album/145486923"
if len(sys.argv) < 2:
    print "usage: python dad.py <douban album link>"
    sys.exit(1)
album = sys.argv[1]
# 豆瓣有img[0-6]共7个图片镜像，这里为简便起见，随便选了一个
large_photo_base = "http://img3.douban.com/view/photo/large/public/p"

try:
    res = urllib2.urlopen(album)
except urllib2.HTTPError as e:
    print "HTTP Error %s : %s" % (e.code, e.reason)
    sys.exit(1)
except urllib2.URLError, e:
    print "Unable to connect remote server."
    sys.exit(1)

content = res.read()
soup = BeautifulSoup(content)

title = soup.title.text.strip()
match = re.match(ur"^(.*)的相册\-(.*)", title)
album_author = match.group(1)
album_title = match.group(2)

print "Album Author : {}".format(album_author.encode("utf8"))
print "Album Name   : {}".format(album_title.encode("utf8"))

# 检测相册是否有多页，是则获取页数
if soup.find("div", "paginator"):
    #photo_total_number = re.search(r"\d+", soup.find("span", "count").text).group()
    #photo_total_page = soup.find("span", "thispage")["data-total-page"]
    photo_total_page = soup.find(
        lambda x: x.has_attr("data-total-page"))["data-total-page"].encode("utf8")
else:
    photo_total_page = 1

if not os.path.exists(album_title):
    os.makedirs(album_title)
for i in xrange(0, int(photo_total_page)):
    page_url = album + "/?start={0}".format(i * 18)
    print "Fetching page [{:<2}] ...".format(i + 1)
    res = urllib2.urlopen(page_url)
    soup = BeautifulSoup(res.read())
    photo_ids = [re.search(r"\d+", x["href"]).group()
                 for x in soup.find_all("a", "photolst_photo")]
    for id in photo_ids:
        large_photo_url = large_photo_base + id.encode("utf8") + ".jpg"
        try:
            res = urllib2.urlopen(large_photo_url)
        except urllib2.HTTPError, e:
            # 如果出现404错误，则有可能是该照片没有大图版，尝试下载正常版。（主要是一些老相册）
            if e.code == 404:
                print "Large photo for {0} is not found, try normal one".format(id)
                res = urllib2.urlopen(
                    large_photo_url.replace("large", "photo"))
            else:
                print "HTTP Error {0} : {1}".format(e.code, e.reason)
                continue

        with open(os.path.join(".", album_title, "{0}.jpg".format(id)), "wb") as f:
            f.write(res.read())
