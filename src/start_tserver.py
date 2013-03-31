#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos

from daemon import runner
from tstmp_server import *
from stmp import *


class TSTMPApp(STMPApp):
    def run(self):
        server = TSTMPServer(self.config, self.logger)
        server.run()

stmpapp = TSTMPApp()
daemon_runner = runner.DaemonRunner(stmpapp)
stmpapp.daemonize(daemon_runner)
daemon_runner.do_action()





