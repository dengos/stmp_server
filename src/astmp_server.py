#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Author: dengos
#

import asyncore
import asynchat
import socket
import logging
import json
import sys
import pdb
from stmp import *
from qsession import Qsession

##
# @brief
# ASTMPServer, a subclass of asyncore.dispatcher, which
# is a sophistic python asynchronization I/O framework.
#
# Usage:
#    config = json.load(open(config_file))
#    logger = logging.getLogger(logger_name)
#    server = ASTMPServer(config, logger)
#    server.run()
#
class ASTMPServer(asyncore.dispatcher):
    ##
    # @brief
    #
    # @param json_config A json object, which contain the configure
    # information.
    # @param logger A log object from logging modular
    #
    # @return a ASTMPServer object
    def __init__(self, json_config, logger):
        asyncore.dispatcher.__init__(self)
        self.config = json_config
        self.logger = logger
        self.message = json.load(open(self.config["message"]))



    def create_listenfd(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((self.config["host"], self.config["port"] ))
        self.listen(self.config["backlog"])
        #

    ##
    # @brief
    # @return None
    def run(self):
        self.create_listenfd()
        asyncore.loop()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # log
            stmp_log = STMPLog(self.logger, addr)
            try:
                handler = ASTMPHandler(sock, addr, self.message, self.config, stmp_log)
            except:
                # ignore all the exception for simplicity
                self.log.write("Unexpected error: {0}".format(sys.exc_info()[0]))


##
# @brief
# ASTMPHandler is used only in ASTMPServer, asyncore framework
# maintain all the handlers for each incomming connected socket
# descripter.
#
class ASTMPHandler(asynchat.async_chat):
    """docstring for STMPHandler"""
    def __init__(self, sock, addr, message, json_config, logger):
        # calling the super class __init__
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr    = addr
        self.ibuffer = []
        self.config  = json_config
        self.message = message
        self.logger  = logger
        # as a handler in stmp server, we expected the message
        # sending from server will be small.
        self.ac_out_buffer_size = 512
        self.timeout = self.config["timeout"]
        self.max_buf_size = self.config["bufsize"]
        # usually, we won't use "\r\n" as the terminator in
        # stmp protocol, but, for simplicity.
        self.set_terminator("\r\n")
        # log a user enter
        self.session = Qsession(self.logger)
        self.logger.write(self.message["enter"])

    ##
    # @brief
    #
    # @param data the receiving data
    #
    # @return None
    def collect_incoming_data(self, data):
        self.ibuffer.append(data)
        if len(self.ibuffer) >= self.max_buf_size:
            self.found_terminator()


    ##
    # @brief
    # There are only two available situation this function
    # will be called.
    # 1. async_chat meet the terminator;
    # 2. the self.ibuffer contain too many data.
    # @return None
    def found_terminator(self):
        data = "".join(self.ibuffer)
        # we say the self.ibuffer have been consumed.
        self.ibuffer = []
        # The session (Qsession) will give response based on
        # the given data.
        # 1. response will send back to client;
        # 2. is_continue tell handler that is this connection should
        #    be closed ?
        response, is_continue = self.session.feed(data)
        if response is not None:
            self.push(response)
        if not is_continue:
            self.close_when_done()


    def handle_close(self):
        self.logger.write(self.message["exit"])
        asynchat.async_chat.handle_close(self)

    def handle_read(self):
        try:
            self.settimeout(self.timeout)
            ret = asynchat.async_chat.handle_read(self)
            # we only need timeout work when read the data from client
            self.settimeout(None)
        except socket.timeout:
            self.logger.write(self.message["timeout"])
            self.close_when_done()
        return ret

