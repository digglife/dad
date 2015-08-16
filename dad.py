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
image_base = "http://img3.douban.com/view/photo/large/public/p"

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

photo_total_number = re.search(r"\d+", soup.find("span", "count").text).group()
photo_total_page = soup.find("span", "thispage")["data-total-page"]
photo_total_page = soup.find(
    lambda x: x.has_attr("data-total-page"))["data-total-page"].encode("utf8")

if not os.path.exists(album_title):
    os.makedirs(album_title)
for i in xrange(0, int(photo_total_page)):
    page_url = album + "/?start={0}".format(i*18)
    print "Fetching page [{:<2}] ...".format(i+1)
    res = urllib2.urlopen(page_url)
    soup = BeautifulSoup(res.read())
    photo_ids = [re.search(r"\d+", x["href"]).group()
                 for x in soup.find_all("a", "photolst_photo")]
    for id in photo_ids:
        large_photo_url = image_base + id.encode("utf8") + ".jpg"
        res = urllib2.urlopen(large_photo_url)
        with open(os.path.join(".",album_title,"{0}.jpg".format(id)), "wb") as f:
            f.write(res.read())

