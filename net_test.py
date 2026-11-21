import socket
class NetDev:
    def __init__(self):
        self.s = None
        self.name=""
        self.port=5000
        self.ps = 0
        self.psb = 0
        self.send_item = bytearray()
        self.recv_item = bytearray()
        self.t = 3

    def nameout(self,v):
        if v != 0:
            self.name += chr(v)
            return
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.t)
        try:
            self.s.connect((f"{self.name}", self.port))
            self.s.setblocking(False)    # ← 足す(接続できた後、1回だけ)
        except OSError:
            self.close(0)  
        self.name = ""               # ← 足す(次の接続用に空に戻す)

    def send_charge(self,v):
        self.send_item.append(v & 0xFF)

    def send(self,v):
        if self.s:  
            try:
                self.s.sendall(bytes(self.send_item))
            except OSError:
                pass
        self.send_item.clear()

    def recving(self):
        if self.s is None:
            return 0
        stat = 0
        try:
            self.recv_item.extend(self.s.recv(1024))
            stat = 1
        except BlockingIOError:
            pass

        return stat

    def rx(self):
        a = 0
        if len(self.recv_item) > 0:
            a = self.recv_item.pop(0)
        return a
    
    def close(self,v):
        if self.s: 
            self.s.close()
            self.s = None

    def portset(self,v):
        if self.ps == 0:
            self.psb = v
            self.ps += 1
        elif self.ps == 1:
            self.psb += (v*256)
            self.ps = 0
            self.port = self.psb

a = NetDev()
a.port = 80                      # ← 足す(今は5000のまま。example.comは80番)
a.name = "example.com"
a.nameout(0)

for ch in b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n":
    a.send_charge(ch)            # ← 足す
a.send(0)                        # ← 足す

# 直す
import time
time.sleep(1)                    # 返事が来るのを待つ

while a.recving():
    print(chr(a.rx()), end="")
print()
a.close(0)