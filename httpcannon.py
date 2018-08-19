#!/usr/bin/env python3

import os, threading, argparse, csv, ssl, http.client, queue
from urllib.parse import urlparse
from fake_useragent import UserAgent
from colorama import Fore, Style

def _worker():
    global self_failed
    global self_succeeded
    while True:
        item = q.get()
        #print(str(item))
        if item is None:
            break
        doworkresults = _dowork(myurlcfg=item)
        if "FAILED" in doworkresults:
            self_failed += 1
        else:
            self_succeeded += 1
        print("{results}".format(results=doworkresults))
        q.task_done()

def _dowork(**kwargs):
    self_urlcfg = kwargs['myurlcfg']
    self_url = self_urlcfg["url"]
    self_urlname = self_urlcfg["urlname"]
    self_scheme = self_urlcfg["scheme"]
    self_timeout = self_urlcfg["timeout"]
    self_useragent = self_urlcfg["useragent"]
    self_netloc = self_urlcfg["netloc"]
    self_path = self_urlcfg["path"]

    try:
        if self_scheme == "https":
            conn = http.client.HTTPSConnection(self_netloc, timeout=self_timeout, context=context)
            conn.request("GET", self_path, headers={"User-Agent" : self_useragent}) #, "Cookie" : "something=something"})
        else:
            conn = http.client.HTTPConnection(self_netloc, timeout=self_timeout)
            conn.request("GET", self_path, headers={"User-Agent" :self_useragent}) #, "Cookie" : "something=something"})
        self_respose_code = conn.getresponse()
        conn.close()
        with outlock:
            if str(self_respose_code.status) not in "200":
                self_state = "FAILED"
                self_color = failed_red
            else:
                self_state = "SUCCESS"
                self_color = succeeded_green
            return("[{statuscode}] {color}{state}{reset} {urlname}".format(urlname=self_urlname, statuscode=self_respose_code.status, state=self_state, color=self_color, reset=reset_color))
            #return("status_code: {statuscode}, url: {url}, netloc: {netloc}, path: {path}, urlname: {urlname}, scheme: {scheme}, timeout: {timeout}, useragent: {useragent}".format(url=self_url, urlname=self_urlname, scheme=self_scheme, timeout=self_timeout, useragent=self_useragent, netloc=self_netloc, path=self_path, statuscode=self_respose_code.status))
    except Exception as e:
        return("[XXX] {color}EXP_FAILED{reset} {urlname} {url}".format(urlname=self_urlname, url=self_url, color=failed_red, reset=reset_color))
        #return("Failed to get url {urlname} {url}\nError Msg: {errormsg}\n".format(urlname=self_urlname, url=self_url, errormsg=e))


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 2.0 python3')
    parser.add_argument('--filename', help='File with the urls to test')
    parser.add_argument('--fileloop', type=int, help='number of times to loop over the file of urls')
    args = parser.parse_args()

    if args.fileloop:
        fileloop = args.fileloop
    else:
        fileloop = 1

    global concurrent
    global context
    global failed_red
    global succeeded_green
    global reset_color
    global self_failed
    global self_succeeded

    self_failed = 0
    self_succeeded = 0
    concurrent = 25 * 2
    context = ssl._create_unverified_context()
    failed_red = Fore.RED
    succeeded_green = Fore.GREEN
    reset_color = Style.RESET_ALL
    self_timeout = 15
    self_fileloopcount = 0
    self_urltotal = 0
    #ua.update()

    for b in range(0,fileloop):
        self_num = 0
        self_urllist = []
        self_urlnamelist = []
        threads = []
        ua = UserAgent()
        global q
        global outlock
        q = queue.Queue(concurrent)
        outlock = threading.Lock()

        if os.path.exists(args.filename):
            with open(args.filename) as csvDataFile:
                csvReader = csv.reader(csvDataFile)
                for row in csvReader:
                    self_urllist.append(row[0].split())
                    self_urlnamelist.append(row[1].split())
        else:
            print("You need to pass in a file: {filename}").format(filename=args.filename)
            exit(1)

        print()


        for z in range(concurrent):
            t = threading.Thread(target=_worker)
            t.start()
            threads.append(t)

        for self_url in self_urllist:
            self_url = str(self_url[0])
            self_urlname = self_urlnamelist[self_num]
            self_urlname = self_urlname[0]
            self_urltotal += 1
            self_num = self_num + 1

            self_useragent = ua.random
            if self_useragent == "":
                self_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"

            self_completeurl = urlparse(self_url)
            self_scheme = self_completeurl.scheme
            self_netloc = self_completeurl.netloc
            self_path = self_completeurl.path + self_completeurl.query + self_completeurl.fragment
            self_urlconfig = {'url':self_url, 'netloc': self_netloc, 'path': self_path, 'urlname': self_urlname, 'scheme': self_scheme, 'useragent': self_useragent, 'timeout': self_timeout}
            q.put(self_urlconfig)
        q.join()
        #print("\n{succeeded} of {urltotal} succeeded\nFailed on {failed}\nprocessed {times}".format(urltotal=self_urltotal, failed=self_failed, succeeded=self_succeeded, times=self_fileloopcount))
        for i in range(concurrent):
            q.put(None)

        for t in threads:
            t.join()
        self_fileloopcount += 1
        print("\n{succeeded} of {urltotal} succeeded\nFailed on {failed}\nProcessed url file {times}\n".format(urltotal=self_urltotal, failed=self_failed, succeeded=self_succeeded, times=self_fileloopcount))

if __name__ == '__main__':
    _main()
