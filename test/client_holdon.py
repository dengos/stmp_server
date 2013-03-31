#!/usr/bin/python

import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 25
s.connect((s.getsockname()[0], port))
try:
  while True:
    # data = raw_input("DATA to transmit:\n")
    #data = lines[k]
    #k += 1
    data = "don't kown"
    s.send(data)
    if data == 'C':
      break
    data = s.recv(4096)
    time.sleep(1)
except socket.timeout:
    pass
