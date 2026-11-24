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
        self.t = 10
        self.closed = False

        self.ls = None
        self.waitport = []

    def nameout(self,v):
        if v != 0:
            self.name += chr(v)
            return
        self.closed = False
        self.recv_item.clear()
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

    def fill(self):                     # 貯める役(ソケットから recv_item へ)
        if self.s is None:
            return
        try:
            d = self.s.recv(1024)
            if d:
                self.recv_item.extend(d)

            else:
                self.closed = True
        except BlockingIOError:
            pass
        except OSError:
            self.closed = True
            

    def recving(self):
        self.fill()
        if self.s is not None and not self.recv_item and self.closed and self.ls is not None:
            self.s.close()
            self.s = None
        return 1 if self.recv_item else 0

    def rx(self):                       # 値だけ返す(1バイト)
        if self.recv_item:
            return self.recv_item.pop(0)
        return 0
    
    def close(self,v):
        if self.s: 
            self.s.close()
            self.s = None
        self.closed = False

    def portset(self,v):
        if self.ps == 0:
            self.psb = v
            self.ps += 1
        elif self.ps == 1:
            self.psb += (v*256)
            self.ps = 0
            self.port = self.psb

    def status(self):       # 0=未接続 1=接続中 2=切断された
        if self.s is None:
            return 0
        return 2 if self.closed else 1


    def ipset(self,v):
        self.waitport.append(v)

    def listen_start(self, v):          # OUT: portset で決めた番号で待ち受け開始
        self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            waitport_made = f"{self.waitport[0]}.{self.waitport[1]}.{self.waitport[2]}.{self.waitport[3]}"
        except:
            waitport_made = "127.0.0.1"
        self.waitport = []

        try:
            self.ls.bind((waitport_made, self.port))
            self.ls.listen(1)
            self.ls.setblocking(False)
        except OSError:
            self.ls.close()
            self.ls = None

    def accepting(self):                # IN: 1=客が来た 0=まだ
        if self.ls is None:
            return 0
        if self.s is not None:
            return 1
        try:
            conn, addr = self.ls.accept()
            conn.setblocking(False)
            self.closed = False
            self.recv_item.clear()
            self.s = conn               # 以降は rx / send などがそのまま使える
            return 1
        except BlockingIOError:
            return 0

    def listen_stop(self, v):
        if self.ls:
            self.ls.close()
            self.ls = None

    def reset(self):
        if self.s:
            try: self.s.close()
            except OSError: pass
        if self.ls:
            try: self.ls.close()
            except OSError: pass
        self.s = None
        self.ls = None
        self.name = ""
        self.port = 5000
        self.ps = 0
        self.psb = 0
        self.send_item.clear()
        self.recv_item.clear()
        self.closed = False
        self.waitport = []