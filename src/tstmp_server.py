#!/usr/bin/env python2
# -*- coding: utf-8  -*-
#
# Author: dengos
#



import time
import socket
import threading
import logging
import sys
import json
from stmp import *
from qsession import Qsession


##
# @brief
# This is a wrap-up function, for threading
def stmp_thread(machine):
    machine.run()


##
# @brief
#
# Usage:
#     config = json.load(open(config_file))
#     logger = logging.getLogger(logger_name)
#     server = TSTMPServer(config, logger)
#     server.run()
#
class TSTMPServer:
    def __init__(self, json_config, logger):
        """docstring for __init__"""
        self.config = json_config
        self.logger = logger
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
    # @return None
    def run(self):
        listenfd = self.create_listenfd()
        while True:
            pair = listenfd.accept()
            if pair is not None:
                conn, addr = pair
                log = STMPLog(self.logger, addr)
                stmp_machine = TSTMPMachine(conn, addr, log, self.message, self.config)
                worker = threading.Thread(target = stmp_thread, args = (stmp_machine, ))
                worker.daemon = True
                worker.start()
                # unlike c unix programming..
                # we don't explicit close the conn here, all the work left
                # for python auto-collector



##
# @brief
# A simple worker object for threading.
# When server accpet a connection from client, a new simple
# worker will be created along with a new thread.
# The main stmp logic is implemented by Qsession class, this
# worker only connect data, feed data to Qsession, sending the
# response back to client.
class TSTMPMachine:
    """docstring for STMPMachine"""
    def __init__(self, conn, addr, logger, message, json_config):
        self.conn = conn
        self.addr = addr
        self.logger  = logger
        self.message = message
        self.config  = json_config
        self.session = Qsession(logger)
        self.timeout = self.config["timeout"]
        self.bufsize = self.config["bufsize"]

    def write(self, msg):
        self.conn.send(msg)

    def read(self):
        try:
            # we only need to monitor the timeout for
            # reading data from client socket
            self.conn.settimeout(self.timeout)
            data = self.conn.recv(self.bufsize)
            self.conn.settimeout(None)
        except socket.timeout:
            self.logger.write(self.message["timeout"])
            data = None
        return data

    def close(self):
        self.conn.close()


    ##
    # @brief
    #
    # @return
    def run(self):
        try:
            self.logger.write(self.message["enter"])
            is_continue = True
            while is_continue:
                data = self.read()
                if data is None:
                    break
                response, is_continue = self.session.feed(data)
                if response is not None:
                    self.write(response)
            self.logger.write(self.message["exit"])
            self.close()
        except:
            self.logger.write("Unexpected error: {0}".format(sys.exc_info())[0])

