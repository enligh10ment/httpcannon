#!/usr/bin/env python

import optparse, os, sys, httplib, socket, ssl, time, subprocess
from urlparse import urlparse
from threading import Thread
from Queue import Queue
from fake_useragent import UserAgent
from datetime import datetime

# splunk query for viewing distribution of random UA assignment
# sourcetype=access_log clientip="YOUR_IP" | stats count(useragent) by useragent

# concurrent = 500
concurrent = 50
ua = UserAgent()
#ua.update()
context = ssl._create_unverified_context()
fails = 0
totalcount = 0
defaultUA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
defaultTimeOut = 15

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def tcpSend(line):
  TCP_IP = ''
  TCP_PORT = ''

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((TCP_IP, TCP_PORT))
  s.send(line)
  s.close()

def current_time():
    return datetime.now().strftime('[%Y/%m/%d %H:%M:%S]')

def doWork():
    while True:
        url = q.get()
        status, url, ourl = getStatus(url)
        doSomethingWithResult(status, url, ourl)
        q.task_done()
        #print str(failcount) + " Failed URLs"

def getStatus(ourl):
    try:
        spliturl = ourl.split(",")
        ourl = spliturl[0] + spliturl[1]
        ourl = str(ourl)
        #print ourl
        url = urlparse(ourl)
        #print  url
        #togetpath = url.path + url.params + url.query + url.fragment
        togetpath = spliturl[1]
        nicename = spliturl[2]
        #print togetpath
        #print url
        myscheme = None
        myscheme = str(url.scheme)
        #print myscheme
        RandomUA = ua.random
        if RandomUA == "":
          RandomUA = defaultUA
        if myscheme in "http":
            conn = httplib.HTTPConnection(url.netloc, timeout=defaultTimeOut)
            #print "in http"
            conn.request("GET", togetpath, headers={"User-Agent" : RandomUA}) #, "Cookie" : "something=something"})
        else:
            conn = httplib.HTTPSConnection(url.netloc, timeout=defaultTimeOut, context=context)
            #print "in https"
            conn.request("GET", togetpath, headers={"User-Agent" : RandomUA}) #, "Cookie" : "something=something"})
        res = conn.getresponse()
        conn.close()
        #print res.msg
        #return res.status, nicename
        return res.status, nicename, ourl
    except:
        return "error", nicename, ourl

def doSomethingWithResult(status, url, ourl):
    # do a check on the status/name here. :)
    status = str(status)
    url = str(url)
    if status in "200":
      pass
      #print "[" + status + "]" + bcolors.OKGREEN  +" SUCCESS " + bcolors.ENDC + url
    elif ("SomeNiceURLName" in url and status in "401") or ("SomeOtherNiceURLName" and status in "401"):
      pass
      #print "[" + status + "]" + bcolors.OKGREEN  +" SUCCESS " + bcolors.ENDC + url
    else:
      print "[" + status + "]" + bcolors.FAIL + " FAILED " + bcolors.ENDC +  url
      global fails
      fails += 1

      global mySplunk
      #print mySplunk
      if 'TRUE' in mySplunk:
        myTime = current_time()
        tcpSend(str(myTime) + " state=FAILED status=\"" + str(status) + "\" urlname=\"" + str(url) + "\" url=\"" + str(ourl) + "\" origin=int env=prod")

print ""

optparser = optparse.OptionParser(prog='http-cannon.py', version='0.1', description='Quickly make http requests and display status response', usage='%prog -f [url file name] -s [TRUE|FALSE] -l [# of times to loop file]')
optparser.add_option('--filename', '-f', dest='filename')
optparser.add_option('--splunk', '-s', dest='splunk', default='FALSE')
optparser.add_option('--fileloop', '-l', dest='fileloop', default='1')
options, arguments = optparser.parse_args()
if options.filename and options.splunk and options.fileloop:
  if not os.path.isfile(options.filename):
    sys.exit('Error: The file does not exist!\n')

  myFilename = options.filename
  mySplunk = options.splunk
  myFileloop = int(options.fileloop)
  myFileloopCount = 0  

  q = Queue(concurrent * 2)

  for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()
  try:
    for z in range(0,myFileloop):
      for url in open(myFilename):
        url=url.strip()
        if not url.startswith("#") and url.strip():
          q.put(url)
          totalcount += 1
      q.join()
      myFileloopCount += 1
      print bcolors.BOLD + myFilename + " has been processed " + str(myFileloopCount) + "/" + str(myFileloop)  + bcolors.ENDC  + "\n"
  except KeyboardInterrupt:
    sys.exit(1)

else:
  optparser.print_help()
  print ""
  sys.exit(1)

# Needed to prevent script from exiting before threads finish, 500ms
time.sleep(0.500)

if fails > 0:
  print ""

print bcolors.BOLD + str(fails) + " failed url tests out of " + str(totalcount) + bcolors.ENDC + "\n"


