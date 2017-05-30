# coding:utf-8

import os, sys, time, random, json
import re, requests, urllib2
import sys

from urllib3.exceptions import NewConnectionError, ConnectionError

reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup

# http://app.mi.com/topList?page=1
# http://app.mi.com/topList?page=42

USER_AGENTS = (
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_0; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:0.9.2) Gecko/20020508 Netscape6/6.1",
    "Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5",
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
    'Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10'
)

APPEND_FILE_PATH = "/Users/bang/Downloads/apks/"


def getURLContent(url='http://app.mi.com/topList?page=1'):
    headers = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://app.mi.com/topList',
        'Cookie': 'JSESSIONID=aaaWYqTT3MMdVfeRHjMev; __utma=127562001.883425548.1452953270.1452953270.1452953270.1; __utmc=127562001; __utmz=127562001.1452953270.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
    }

    headers[
        'User-Agent'] = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"  # USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]

    try:
        r = requests.get(url, headers=headers, timeout=1)
        r.raise_for_status()
    except requests.RequestException as e:
        print e
        return None
    else:
        print r.encoding
        return r.content


def getURL(url):
    print "[Download]%s" % url
    headers = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://app.mi.com/topList'
    }
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"

    try:
        r = requests.get(url, headers=headers, timeout=1)
        r.raise_for_status()
    except requests.RequestException as e:
        print e
        return None
    else:
        print r.encoding
        return r


def write2file(filename, requestshandle):
    if not requestshandle:
        print "[ERROR] No available requests", requestshandle
    else:
        with open(filename, "wb+") as fp:
            fp.write(requestshandle.content)


def append2file(filename, string):
    with open(filename, "a+") as fp:
        fp.write(string)
        fp.write("\n")
        fp.close()


def fetchApkinfoFromWebpage(weburl="http://app.mi.com/topList?page=1"):
    apklist = []
    html_doc = getURLContent(weburl)
    soup = BeautifulSoup(html_doc, from_encoding="utf-8")
    for item in soup.findAll(attrs={"class": "applist"})[0]:
        # print item

        try:
            item_soup = BeautifulSoup(str(item))
            # http://file.market.xiaomi.com/thumbnail/PNG/l62/AppStore/0a4e5f4d25ff24f2237ba83be3dd43205cbf1b5b4
            # http://file.market.xiaomi.com/thumbnail/PNG/l114/AppStore/0a4e5f4d25ff24f2237ba83be3dd43205cbf1b5b4
            apk_icon = apk_name = item_soup.find_all('img')[0].get('data-src')
            apk_name_cn = item_soup.find_all('h5')[
                0].get_text()  # item_soup.find_all('a')[-2].get_text() #item_soup.find_all('h5')[0].get_text() ##apk_name = item_soup.find_all('img')[0].get('alt').encode('utf-8')
            apk_webpage = "http://app.mi.com" + item_soup.find_all('a')[0].get('href')
            apk_category = getCategory(item_soup)
            apk_package_id = apk_webpage.split("/")[-1]
            apk_id = get_apk_id(apk_package_id)
            apk_url = get_apk_real_downloadurl(apk_id)
            # apk_name_en = BeautifulSoup(getURLContent(apk_webpage)).findAll(attrs={"class":"special-li"})[0].get_text()
            apk_name_en = apk_url.split("/")[-1].replace(".apk", "")
            print '\n\n---------------------------开始下载 : '+apk_name_cn+'----------------------------------------------'
            print apk_id, apk_name_en, apk_name_cn, apk_url, apk_webpage, apk_icon
            apkstring = "|%s|%s|%s|%s|%s|%s|%s|" % (apk_id, apk_name_en, apk_name_cn, apk_url, apk_webpage, apk_icon,apk_category)

            if int(apk_category) != 27 and 16 <= int(apk_category) <= 29:
                print '---------------------------跳过游戏的下载 : ' + apk_name_cn + '----------------------------------------------'
                continue
            else:
                append2file(APPEND_FILE_PATH + "apkinfo.txt", apkstring)
                apklist.append(apkstring)
                downloadApk(apk_url)

        except urllib2.HTTPError as e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            append2file(APPEND_FILE_PATH + "errorInfo.txt", apkstring)
        except urllib2.URLError as e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            append2file(APPEND_FILE_PATH + "errorInfo.txt", apkstring)
        except NewConnectionError as e:
            print 'We failed to NewConnection.'
            print 'Reason: ', e.message
            append2file(APPEND_FILE_PATH + "errorInfo.txt", apkstring)
        except ConnectionError as e:
            print 'We failed to ConnectionError.'
            print 'Reason: ', e.message
            append2file(APPEND_FILE_PATH + "errorInfo.txt", apkstring)
        except Exception as e:
            print 'We failed to ConnectionError.'
            print 'Reason: ', e.message
            append2file(APPEND_FILE_PATH + "errorInfo.txt", apkstring)
        else:
            print '---------------------------结束下载 : '+apk_name_cn+'----------------------------------------------'
    # print len(apklist)
    return apklist


def getCategory(item_soup):
    categoryHref = item_soup.find_all('p')[0].contents[0].get('href')
    return categoryHref[categoryHref.rindex('/')+1:len(categoryHref)]


def get_apk_id(apkid):
    apkurl_prefix = "http://app.mi.com/"
    s = requests.session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate,sdch",
        "Host": "app.mi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    s.headers.update(headers)
    data = ""
    try:
        resp = s.get(apkurl_prefix + str(apkid), timeout=1000, allow_redirects=False)
        content = resp.content
        # print content
        template = '<a href="(/download/.*?)" class="download">(.*?)</a>'
        postFixPattern = re.compile(template)
        apkurl_postFix = re.search(postFixPattern, content).group(1)
        split = re.search(postFixPattern, content).group(1).split('/')
        data = split[split.__len__() - 1]
    except Exception as e:
        print e.message
    except ConnectionError as e:
        print e.message

    return data


def get_apk_real_downloadurl(apkid):
    apkurl_prefix = "http://app.mi.com/download/"
    s = requests.session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate,sdch",
        "Host": "app.mi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    s.headers.update(headers)
    redirectUrl = apkurl_prefix + apkid

    downloadResp = s.get(redirectUrl, timeout=1000, allow_redirects=False)
    return downloadResp.headers['Location']


def downloadApk(apk_url):
    url = apk_url

    local_file_name = url.split('/')[-1]
    local_file_name = APPEND_FILE_PATH + local_file_name
    localFileSize = os.path.getsize(local_file_name)

    print 'url: '+ url
    u = urllib2.urlopen(url)
    netFileSize = u.headers.dict['content-length']
    if int(netFileSize) == localFileSize:
        #如果值相等，说明下载过了，直接跳过
        print "----------------------------已经下载过,跳过-----------------------------------------------"
    else:
        realDownload(local_file_name, u)

    pass


def realDownload(file_name, u):
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()

def error_test2():
    raise NewConnectionError('no pool', 'test one')

if __name__ == "__main__":
    allapklist = []
    # gameswebpage = "http://app.mi.com/gTopList"
    appswebpages = ["http://app.mi.com/topList?page=%d" % i for i in xrange(1, 21)]
    # appswebpages.insert(0, gameswebpage)
    #
    for weburl in appswebpages:
        apklist = fetchApkinfoFromWebpage(weburl)
        allapklist.extend(apklist)
    print len(allapklist)
