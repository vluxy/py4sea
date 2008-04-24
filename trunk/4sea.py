#!/usr/bin/env python
# encoding: utf-8
# Junda Liu

import sys,os
import webbrowser
import SocketServer, BaseHTTPServer

def pub(name, txt):
    """call avahi to publish our svc, based on name and other info"""
    (pin, pout) = os.popen2("avahi-publish -s "+name+" _4sea._udp 43210 "+txt)
    print pout.read()

def getsvc():
    """call avahi browse and return 4sea svc list"""
    (pin, pout) = os.popen2("avahi-browse _4sea._udp")
    print pout.read()

class myHTTPhandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_error(404, "File not found")
        pass
    def do_POST(self):
        pass

class myHTTPserver(BaseHTTPServer.HTTPServer): pass

def main():
    pub("myself test", "this is txt")
    getsvc()
    
    httpd = myHTTPserver(('',8080),myHTTPhandler)
    thread.start_new_thread(httpd.handle_request,())
    webbrowser.open_new("http://localhost:8080")
    
    #pass

if __name__ == '__main__':
    main()
