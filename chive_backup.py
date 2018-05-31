#!/usr/bin/env python
from __future__ import division
import sys
import subprocess
from datetime import datetime
import urllib2, os, sys, math, urllib
from bs4 import BeautifulSoup
import credentials

#SYNTAX
#chive_backup.py "Start page" "End page" "log name"
#credentials has log_dir and base_dir

logFile = credentials.log_dir+sys.argv[3]
firstPage = int(sys.argv[1])
lastPage = int(sys.argv[2])

file = open(logFile,"a")
file.write("\n"+ "START: " + str(firstPage) + " END: " + str(lastPage))
file.close()

baseDir = credentials.base_dir
baseUrl = "http://thechive.com/category/sexy-girls/page/"
filter = ("Photo", "Photos", "photos", "photo", "GIF", "GIFS", "gif", "gifs", "GIFs", "Gifs", "Gif")


class outputcolors:
        OKGREEN = '\033[92m'
        OKBLUE = '\033[94m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

def getStatus(url):
    try:
        connection = urllib2.urlopen(url)
        code = connection.getcode()
        connection.close()
        return code
    except urllib2.HTTPError, e:
        return e.getcode()

def ensureDir(f):
        if not os.path.exists(f):
                os.makedirs(f)

def getSoup(url):
    try:
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url)), "lxml")
    except urllib2.HTTPError, e:
        print("retrying in 5s")
        time.sleep(5)
        return getSoup(url)

def fileDl(url, dir, prepend, fileName = "?"):
    if fileName == "?":
        fileName = url.split('/')[-1]
        request = urllib2.Request(url)
        u = urllib2.urlopen(request)
        meta = u.info()
        fileSize = -1
        try:
                fileSize = int(meta.getheaders("Content-Length")[0])
        except Exception:
                pass
        if os.path.exists(dir + fileName):
                if os.stat(dir + fileName).st_size == fileSize:
                        print(prepend + outputcolors.OKBLUE + "File already downloaded!" + outputcolors.ENDC)
                        file = open(logFile,"a")
                        file.write("X")
                        file.close()
                        return 42
        	else:
                	print(prepend + outputcolors.WARNING + "File downloaded but not fully! Restarting download..." + outputcolors.ENDC)
    else:
        print(prepend + outputcolors.WARNING + "Downloading file..." + outputcolors.ENDC)
        fileHandle = open(dir + fileName, 'wb')
        print(prepend + ("Downloading: %s Bytes: %s" % (fileName, "???" if (fileSize == -1) else fileSize)))
        fileSizeDl = 0
        blockSize = 65536
        while True:
                buffer = u.read(blockSize)
                if not buffer:
                        break
                fileSizeDl += len(buffer)
                fileHandle.write(buffer)
                status = prepend + r"%12d  [%3.2f%%]" % (fileSizeDl, -1.0 if (fileSize == -1) else (fileSizeDl * 100. / fileSize))
                status = "\r" + status
                print status,
        fileHandle.close()
        file = open(logFile,"a")
        file.write("DL ")
        file.close()
        print("\n" + prepend + outputcolors.OKGREEN + "Done :)" + outputcolors.ENDC)

while True:

    for page in range(firstPage, lastPage + 1):
        file = open(logFile,"a")
        file.write("\n"+ str(page) + " " + str(datetime.now()) + " ")
        file.close()
        pageSoup = getSoup(baseUrl + str(page) + "/")
        print("Page " + str(page) + " of " + str(lastPage))
        for article in pageSoup.findAll('article', { "role" : "article" }):
            date = article.find('time')['datetime']
            h3 = article.find('h3', { "class" : "post-title entry-title card-title" })
            name = h3.text.strip()
            file = open(logFile,"a")
            file.write( "\n"+ str(datetime.now())+ " "+ name.encode('utf-8') + " " + datetime.strptime(date, '%Y-%m-%d').strftime("%Y/%m/%d") +" ")
            file.close()
            url = h3.find('a')['href']
            if any(x in name for x in filter):
                print("\tName: " + name + "\n\t\tDate: " + date)
                dateFolder = "NonParsable/"
                try:
                    dateFolder = datetime.strptime(date, '%Y-%m-%d').strftime("%Y/%m/%d/")
                except ValueError:
                    print("\t\tGoing to NonParsable folder")
                ensureDir(baseDir + dateFolder + name + "/")
                postSoup = getSoup(url)
                for countTag in postSoup.findAll('div', { "class" : "count-tag" }):
                    try:
                        img = countTag.parent.find('img')
                        imgSrc = img['src'].split('?')[0] + "?quality=100"
                        imgName = img['src'].split('?')[0].split('/')[-1]
                        if any(x in img['class'] for x in { "gif-animate" }):
                            imgSrc = img['data-gifsrc'].split('?')[0]
                            imgName = img['data-gifsrc'].split('?')[0].split('/')[-1]
                        print("\t\t\tImage" + countTag.text + ": " + imgSrc)
                        fileDl(imgSrc, baseDir + dateFolder + name + "/", "\t\t\t\t", imgName)
                    except:

                        pass
