#!/usr/bin/env python2
# -*- coding: utf-8  -*-
#




import daemon
import time
import socket
import threading
import logging
from stmp_log import STMPLog
from qsession import Qsession


class TSTMPServer:
    def __init__(self, json_config):
        """docstring for __init__"""
        self.config = json_config
        self.setup()

    def setup(self):
        # 准备日志对象
        logging.basicConfig(format=self.config["log_format"], \
                filename=self.config["log_file"])
        self.logger = logging.getLogger(self.config["server_name"])
        self.message = json.load(open(self.config["message"]))


    def create_listenfd(self):
        listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listenfd.bind((self.config["host"], self.config["port"]))
        listenfd.listen(self.config["backlog"])
        return listenfd


    ##
    # @brief
    #
    # @return
    def run(self):
        listenfd = self.create_listenfd()
        while True:
            pair = listenfd.accept()
            if pair is not None:
                conn, addr = pair
                log = STMPLog(self.logger, addr)
                stmp_machine = STMPMachine(conn, addr, log, self.message, self.config)
                worker = threading.Thread(target = stmp_machine.run, args = (stmp_machine, ))
                worker.daemon = True
                worker.start()
                # 主线程不需要 close conn ?



class STMPMachine:
    """docstring for STMPMachine"""
    def __init__(self, conn, addr, log, message, json_config):
        self.conn = conn
        self.addr = addr
        self.log  = log
        self.message = message
        self.config  = json_config
        self.session = Qsession(log)
        self.timeout = self.config["timeout"]
        self.bufsize = self.config["bufsize"]

    def write(self, msg):
        self.send(msg)

    def read(self):
        # timeout 只有在接收用户数据时候需要考虑
        self.conn.settimeout(self.timeout)
        try:
            data = self.conn.recv(bufsize)
        except socket.timeout:
            # 直接设置为None, data中应该没有数据??
            self.log.write(self.message["timeout"])
            data = None
        self.conn.settimeout(None)
        return data

    def close(self):
        self.conn.close()


    def run(self):
        self.log.write(self.message["enter"])
        is_continue = True
        while is_continue:
            data = self.read()
            # read None 意味着超时
            if data is None:
                break
            response, is_continue = self.session.feed(data)
            if response is not None:
                self.write(response)
        self.log.write(self.message["exit"])
        self.close()


def main():
    pass

#with daemon.DaemonContext():
#    pass

if __name__ == "__main__":
    main()



