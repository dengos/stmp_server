#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos
#

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
    def __init__(self, config, logger):
        self.stdin_path = "/dev/null"
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.config = config
        self.pidfile_path = config["pid_file"]
        self.pidfile_timeout = 5
        self.logger = logger

