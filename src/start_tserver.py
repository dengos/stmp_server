#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos

import logging
import time
import asyncore
import asynchat
import socket
import json
import os
from daemon import runner
from tstmp_server import *
from stmp import *

JSON_CONFIG = "./server.config.json"


class TSTMPApp(STMPApp):
    def run(self):
        server = TSTMPServer(self.config, self.logger)
        server.run()

config = json.load(open(JSON_CONFIG))
current_path = os.path.abspath('../')
config["mail_dir"] = current_path + "mails/"
config["message"]  = current_path + "src/message.json"
logger = logging.getLogger(config["server_name"])
formatter = logging.Formatter(config["log_format"])
handler = logging.FileHandler(config["log_file"])
handler.setFormatter(formatter)
logger.addHandler(handler)

app = TSTMPApp(config, logger)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()





