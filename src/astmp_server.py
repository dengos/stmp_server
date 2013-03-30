#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import asyncore
import asynchat
import socket
import logging
import json
import sys
import pdb
from stmp_log import STMPLog
from qsession import Qsession
from daemon import Daemon

##
# @brief
class ASTMPServer(asyncore.dispatcher):
    """docstring for STMPServer"""
    def __init__(self, json_config):
        asyncore.dispatcher.__init__(self)
        self.config = json_config
        self.setup()

    def setup(self):
        # 准备日志对象
        logging.basicConfig(format=self.config["log_format"].encode("utf-8"), \
                filename=self.config["log_file"])
        self.logger = logging.getLogger(self.config["server_name"])
        # 准备监听socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.config["host"], self.config["port"] ))
        self.listen(self.config["backlog"])
        self.message = json.load(open(self.config["message"]))
        #

    def run(self):
        asyncore.loop()

    ##
    # @brief
    #
    # @return
    def handle_accept(self):
        """docstring for handle_accpet"""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # log
            handler = ASTMPHandler(sock, addr, self.message, self.config)


##
# @brief
class ASTMPHandler(asynchat.async_chat):
    """docstring for STMPHandler"""
    def __init__(self, sock, addr, message, json_config):
        asynchat.async_chat.__init__(self, sock=sock)
        # 创建STMP 日志对象
        self.addr = addr
        self.ibuffer = []
        self.config = json_config
        self.message = message
        self.log = STMPLog(logging.getLogger(self.config["server_name"]), self.addr)
        # 服务器回应数据很小
        self.ac_out_buffer_size = 512

        self.init()
        # 初始终止条件
        # self.set_terminator("\r\n")

    def init(self):
        """docstring for init"""
        self.log.write(self.message["enter"])
        self.session = Qsession(self.log)
        self.timeout = self.config["timeout"]
        self.max_buf_size = self.config["bufsize"]
        # ASTMPHandler 的默认状态是一直接收数据, 当ibuffer中数据大于限定值时,
        # 由collect_incomming_data()　负责调用found_terminator()
        self.set_terminator("\r\n")



    ##
    # @brief
    #
    # @param data
    #
    # @return
    def collect_incoming_data(self, data):
        """docstring for collect_incoming_data"""
        self.ibuffer.append(data)
        if len(self.ibuffer) >= self.max_buf_size:
            self.found_terminator()


    ##
    # @brief
    #
    # @return
    def found_terminator(self):
        # 形成字串, 清空ibuffer
        data = "".join(self.ibuffer)
        self.ibuffer = []
        # Qsession 负责STMP协议的逻辑部分
        response, is_continue = self.session.feed(data)
        # response 为None时表示本次无需响应, 可能是由于当前待
        # 接收数据不完整
        if response is not None:
            self.push(response)
        if not is_continue:
        # 执行关闭, 效果是待发送数据发送完毕, 则关闭对应链接
            self.close_when_done()


    def handle_close(self):
        self.log.write(self.message["exit"])
        asynchat.async_chat.handle_close(self)
        #super(ASTMPHandler, self).handle_close()

    def handle_read(self):
        # timeout 只有在接收用户数据时候需要考虑
        self.settimeout(self.timeout)
        try:
            ret = asynchat.async_chat.handle_read(self)
            #ret = super(ASTMPHandler, self).handle_read()
        except socket.timeout:
            self.log.write(self.message["timeout"])
            self.close_when_done()
        except socket.error:
            self.log.write("socket error")
            self.close_when_done()
        self.settimeout(None)
        return ret

class STMPDaemon(Daemon):
    """docstring for STMPDaemon"""
    def run(self):
        pdb.set_trace()
        with open("server.config.json", "r") as config:
            stmp = ASTMPServer(config)
            asyncore.loop()



if __name__ == "__main__":
    stmp_daemon = STMPDaemon('/tmp/stmp-daemon.pid')
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            stmp_daemon.start()
        elif sys.argv[1] == 'stop':
            stmp_daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.restart()
        else:
            print "Unkown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
