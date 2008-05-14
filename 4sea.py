#!/usr/bin/env python
# encoding: utf-8
# Junda Liu

import sys,os
import webbrowser, urllib, socket
import SocketServer, BaseHTTPServer, SimpleHTTPServer

gmyname = ""
def pub(name, txt):
    """call avahi to publish our svc, based on name and other info
    avahi-publish -s name _p2pchat._udp portnum hereistxt &"""
    (pin, pout) = os.popen2("avahi-publish -s "+name.replace(" ", "_")+" _p2pchat._udp 43210 "+txt.replace(" ","_")+" &")
    (pin, pout) = os.popen2("python chatsvr.py 43210 &")
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
    #pout = open("webui/mockavahi.txt")
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
                newsvc["txt"] = wdlist[3][1:-2] #must have txt!!!
                #newsvc["txt"] = newsvc["txt"].split()[1][1:-1] #must have txt!!! otherwise this has error
                flag = False
                (newsvc["mcxt"], newsvc["mtag"])=getMutual(newsvc["name"],newsvc["txt"])
                svclist.append(newsvc)
                try:
                    f=open(newsvc["name"]+".ip")
                    f.close()
                except IOError:
                    f=open(newsvc["name"]+".ip",'w')
                    f.write(newsvc["address"]+':'+newsvc["port"])
                    f.close()
    pout.close
    return svclist
def getMutual(name, txt):
    try:
        f=open(name+".dat")
        ret = (f.readline(),f.readline())
        f.close()
        return ret
    except IOError:
        try:
            myf = open("myself.dat")
            mycxt = myf.readline()[:-1].split(',')#trim \n
            mytag = myf.readline()[:-1].split(',')
            myf.close()
            tmp = txt.split(';')
            cxt = tmp[0].split(',')
            tag = tmp[1].split(',')
            #print mycxt,mytag,cxt,tag
            f=open(name+".dat","a")
            for e in cxt:
                if e in mycxt:
                    f.write(e+',')
            f.write('\n')
            for e in tag:
                if e in mytag:
                    f.write(e+',')
            f.write('\n')
            f.close()
            f=open(name+".dat")
            ret = (f.readline(),f.readline())
            f.close()
            return ret 
        except IOError:
            return ("","")
        
def formatdata(svclist):
    ret = '<table width="100%"><thead><tr><th>Name</th><th>Mutual Contacts</th><th>Mutual Tags</th></tr></thead><tbody>'
    for svc in svclist:
        ret += '<tr><td>'+svc["name"]+'</td>'
        ret += '<td>'+svc["mcxt"]+'</td>'
        ret += '<td>'+svc["mtag"]+'</td>'
        ret += '</tr>'
    ret += '</tbody></table>'
    return ret

def sendchat(name, msg):
    #print 'name='+name
    addr = open(name+".ip").read().split(':')
    sendudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendudp.sendto(gmyname+':'+msg.split('=')[1]+'\n',(addr[0],int(addr[1])))
    sendudp.close()
    #print addr
def formtags(taglist):
    ret = ''
    for tag in taglist:
        ret+='<div>'+tag+'</div>'
    return ret
class myHTTPhandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("frlist"):
            result = formatdata(getsvc())
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(result))
            self.end_headers()
            self.wfile.write(result)
            return
        if self.path.endswith(".tags"):
            if self.path.endswith("my.tags"):
                myf = open("myself.dat")
            else:
                myf = open("taglist.dat")
            myf.readline()#skip first line of contacts
            mytag = myf.readline()[:-1].split(',')
            myf.close()
            result = formtags(mytag)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(result))
            self.end_headers()
            self.wfile.write(result)
            return
        if self.path.endswith("facebook"):
            os.system("python facebook.py")
            return
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        #self.send_error(404, "File not found")
        #pass
    def do_POST(self):
        if self.path.endswith(".dat"):
            length=int(self.headers.getheader('content-length'))
            request = self.rfile.read(length)
            #print request
            f=open(self.path[1:],'a')
            f.write('<br>'+urllib.unquote_plus(request).replace('=',':'))
            f.close()
            #print 'path='+self.path
            sendchat(self.path[1:-4],request)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(request))
            self.end_headers()
            self.wfile.write(request)

class myHTTPserver(BaseHTTPServer.HTTPServer): pass

def main(name):
    mycxt = "Eric Brewer,Junda Liu,Lin Ning,Gunho Lee,Steve Jobs,Bill Gates"
    mytag = "Berkeley,Star Wars,iPhone,Acura MDX,N810,PSP,Guitar Hero"
    try:
        myf = open("myself.dat")
        mycxt = myf.readline()[:-1]
        mytag = myf.readline()[:-1]
        myf.close()
    except IOError:
        myf = open("myself.dat","w")
        myf.write(mycxt.replace(" ","_") + "\n" + mytag.replace(" ","_") + "\n")
        myf.close()
    pub(name, mycxt + ";" + mytag) #pub will replace " " by "_"
    myf=open("taglist.dat",'w')
    myf.write("taglist\nAcura,Audi,Benz,BMW,Buick,Cadillac,Chevy,Ford,GMC,Honda,Infiniti,Jeep,Lexus,Nissan,Toyota,VW\n")
    myf.close()

    httpd = myHTTPserver(('',8080),myHTTPhandler)
    #thread.start_new_thread(httpd.handle_request,())
    webbrowser.open_new("http://localhost:8080/webui/index.html")
    httpd.serve_forever()
    #pass

if __name__ == '__main__':
    if (len(sys.argv)>1):
        name = sys.argv[1]
    else:
        name = socket.gethostname()
    gmyname = name.replace(" ", "_")
    main(name)
