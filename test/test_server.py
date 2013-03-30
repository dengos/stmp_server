import os
import threading

max_cnt = 5

def conn():
  os.system("python2 client_holdon.py")

for i in range(max_cnt):
  t = threading.Thread( target = conn )
  t.setDaemon(1)
  t.start()

