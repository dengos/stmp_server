#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos
#

import os
import json
import logging

JSON_CONFIG = "../config.json"

##
# @brief
# A simple wrap-up for logging utility
class STMPLog:
    def __init__(self, logger, addr):
        self.log = logger
        self.prefix = "{0}:{1}".format(addr[0], addr[1])

    def write(self, msg):
        self.log.warning(self.prefix + " " + msg)


##
# @brief
# STMPApp class is very important!!
# We prepare the nesssary  setting or data for
# python-daemon lib in this class.
class STMPApp:
    def __init__(self):
        self.stdin_path = "/dev/null"
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.config = json.load(open(JSON_CONFIG))
        path = os.path.abspath('../')
        self.config["mail_dir"] = path + "/mails/"
        self.config["message"]  = path + "/message.json"
        self.pidfile_path = self.config["pid_file"]
        self.pidfile_timeout = 5


    def daemonize(self, daemon_runner):
        self.logger = logging.getLogger(self.config["server_name"])
        formatter = logging.Formatter(self.config["log_format"])
        handler = logging.FileHandler(self.config["log_file"])
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        daemon_runner.daemon_context.files_preserve=[handler.stream]




