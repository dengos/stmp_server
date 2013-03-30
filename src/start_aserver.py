#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: dengos
#

import logging
import time
import asyncore
import asynchat
import socket
import json
import os
from daemon import runner
from astmp_server import *
from stmp import *

JSON_CONFIG = "/home/dengos/stmp/test/server.config.json"


class ASTMPApp(STMPApp):
    def run(self):
        server = ASTMPServer(self.config, self.logger)
        asyncore.loop()

config = json.load(open(JSON_CONFIG))
current_path = os.path.abspath('../')
config["mail_dir"] = current_path + "mails/"
config["message"]  = current_path + "src/message.json"
logger = logging.getLogger(config["server_name"])
formatter = logging.Formatter(config["log_format"])
handler = logging.FileHandler(config["log_file"])
handler.setFormatter(formatter)
logger.addHandler(handler)

app = ASTMPApp(config, logger)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()





