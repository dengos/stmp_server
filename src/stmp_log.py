#!/usr/bin/env python2
#


from logging import Logger
import pdb

class STMPLog:
    """docstring for STMPLog"""
    def __init__(self, logger, addr):
        self.log = logger
        self.prefix = "{0}:{1}".format(addr[0], addr[1])

    def write(self, msg):
        self.log.warning(self.prefix + msg)







