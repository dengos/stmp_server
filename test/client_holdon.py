#!/usr/bin/python

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 8080
s.connect((s.getsockname()[0], port))
try:
  while True:
    data = raw_input("DATA to transmit:\n")
    #data = lines[k]
    #k += 1
    s.send(data)
    if data == 'C':
      break
    data = s.recv(4096)
except socket.timeout:
    pass
