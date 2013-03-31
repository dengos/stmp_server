#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos
#

from daemon import runner
from astmp_server import *
from stmp import *


class ASTMPApp(STMPApp):
    def run(self):
        server = ASTMPServer(self.config, self.logger)
        server.run()


stmpapp = ASTMPApp()
daemon_runner = runner.DaemonRunner(stmpapp)
stmpapp.daemonize(daemon_runner)
daemon_runner.do_action()





