#!/usr/bin/python 
import os, sys, time
import SocketServer, urllib
class myhandler(SocketServer.DatagramRequestHandler):
    def handle(self):
        msg = self.rfile.readline()
        f=open(msg.split(':')[0]+'.dat','a')
        f.write('<br>'+urllib.unquote_plus(msg[:-1]))
        f.close()
class myserver(SocketServer.ThreadingUDPServer):
    pass

if __name__ == "__main__":
    udpd=myserver(('',43210),myhandler)
    udpd.serve_forever()
    
    #proxyd.serve_forever()
    #thread.start_new_thread(proxyd.serve_forever,())
    #if input('Input exit to terminate: ')=='exit': exit()



