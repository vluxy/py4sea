#!/usr/bin/env python
# encoding: utf-8
# Junda Liu

import sys,os,thread
import webbrowser
import SocketServer, BaseHTTPServer

def pub(name, txt):
    """call avahi to publish our svc, based on name and other info
    avahi-publish -s name _p2pchat._udp portnum hereistxt &"""
    (pin, pout) = os.popen2("avahi-publish -s "+name+" _p2pchat._udp 43210 "+txt+" &")
    #print pout.read()

def getsvc():
    """call avahi browse and return 4sea svc list
    avahi-browse -t -r -k -l _p2pchat._udp
    result looks like:
    + wlan0 IPv4 n800web          _p2pchat._udp     local
    = wlan0 IPv4 n800web          _p2pchat._udp     local
      hostname = [Nokia-N800-50-2.local]
      address = [192.168.1.70]
      port = [8080]
      txt = ["org.freedesktop.Avahi.cookie=1853033450" "hereistxt"]
    """
    (pin, pout) = os.popen2("avahi-browse -t -r -k -l _p2pchat._udp")
    flag = False
    svclist = []
    for line in pout.readlines():
        wdlist = line.split()
        if wdlist[0]=="=" and len(wdlist) > 5:
            if wdlist[4] == "_p2pchat._udp":
                flag = True
                newsvc = {}
                newsvc["name"] = wdlist[3]
        elif flag:
            newsvc[wdlist[0]] = wdlist[2][1:-1] #trim [ and ]
            if wdlist[0]=="txt":
                newsvc["txt"] = newsvc["txt"].split()[1][1:-1] #must have txt!!! otherwise this has error
                flag = False
                svclist.append(newsvc)
    return svclist

def formatdata(svclist):
    return str(svclist)

class myHTTPhandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("favicon.ico"):
            return
        if self.path.endswith("data"):
            result = formatdata(getsvc())
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(result))
            self.end_headers()
            self.wfile.write(result)
        #self.send_error(404, "File not found")
        pass
    def do_POST(self):
        pass

class myHTTPserver(BaseHTTPServer.HTTPServer): pass

def main():
    #pub("myself test", "this is txt")
    #getsvc()
    
    httpd = myHTTPserver(('',8080),myHTTPhandler)
    thread.start_new_thread(httpd.handle_request,())
    webbrowser.open_new("http://localhost:8080/data")
    
    #pass

if __name__ == '__main__':
    main()
