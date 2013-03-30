#!/usr/bin/env python2


import logging
import time
import asyncore
import asynchat
import socket
import json

from daemon import runner
from astmp_server import *

class EchoHandler(asyncore.dispatcher_with_send):
    """docstring for EchoHandler"""
    def handle_read(self):
        """docstring for handle_read"""
        data = self.recv(8192)
        if data:
            self.send(data)

class EchoAHandler(asynchat.async_chat):
    """docstring for EchoAHandler"""
    def __init__(self, sock):
        """docstring for __init__"""
        asynchat.async_chat.__init__(self, sock=sock)
        self.ibuffer =[]
        self.set_terminator("\r\n")

    def collect_incoming_data(self, data):
        """docstring for collect_incomming_data"""
        self.ibuffer.append(data)

    def found_terminator(self):
        """docstring for found_terminator"""
        data = "".join(self.ibuffer)
        self.push(data)
        self.ibuffer = []



class EchoServer(asyncore.dispatcher):
    """docstring for EchoServer"""
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        """docstring for handle_accept"""
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            #handler = EchoHandler(sock)
            handler = EchoAHandler(sock)






class App:
    """docstring for App"""
    def __init__(self, logger):
        self.stdin_path = "/dev/null"
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/var/run/testdaemon/testdaemon.pid'
        self.pidfile_timeout = 5
        self.logger = logger

    def run(self):
        config = json.load(open("/home/dengos/stmp/test/server.config.json"))
        server = ASTMPServer(config, self.logger)
        #server = EchoServer('localhost', 8080)
        asyncore.loop()

logger = logging.getLogger("DaemonLog")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/testdaemon/testdaemon.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = App(logger)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()





