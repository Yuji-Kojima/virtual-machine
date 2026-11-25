import socket

class Connect:
    def __init__(self):
        self.s = None
        self.send_item = bytearray()
        self.recv_item = bytearray()
        self.closed = False

class NetDev:
    def __init__(self):
        self.conns = []
        self.name=""
        self.port=5000
        self.ps = 0
        self.psb = 0
        self.t = 10
        self.ls = None
        self.waitport = []
        self.cur = None

    def _c(self):#NetDevが使う部品。VMからは呼ばない
        if self.cur is not None and self.cur < len(self.conns):
            return self.conns[self.cur]
        return None

    def nameout(self,v):
        if v != 0:
            self.name += chr(v)
            return
        c = Connect() #クラスを入れる
        c.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.s.settimeout(self.t)
        try:
            c.s.connect((f"{self.name}", self.port))
            c.s.setblocking(False)    # ← 足す(接続できた後、1回だけ)
            self.conns.append(c)
            self.cur = len(self.conns) - 1
        except OSError:
            c.s.close()  
        self.name = ""               # ← 足す(次の接続用に空に戻す)

    def send_charge(self,v):
        c = self._c()
        if c:
            c.send_item.append(v & 0xFF)

    def send(self,v):
        c = self._c()
        if c:  
            try:
                c.s.sendall(bytes(c.send_item))
            except OSError:
                pass
            c.send_item.clear()

    def fill(self): # 貯める役(ソケットから recv_item へ)
        c = self._c()                 
        if c is None:
            return
        try:
            d = c.s.recv(1024)
            if d:
                c.recv_item.extend(d)

            else:
                c.closed = True
        except BlockingIOError:
            pass
        except OSError:
            c.closed = True

    def recving(self):
        self.fill()
        c = self._c()
        if c is None:
            return 0
        return 1 if c.recv_item else 0

    def rx(self):                       # 値だけ返す(1バイト)
        c = self._c()
        if c and c.recv_item:
            return c.recv_item.pop(0)
        return 0
    
    def close(self,v):
        c = self._c()
        if c is None:
            return
        try:
            c.s.close()
        except OSError:
            pass
        del self.conns[self.cur]
        if not self.conns:
            self.cur = None
        elif self.cur >= len(self.conns):
            self.cur = len(self.conns) - 1
        

    def portset(self,v):
        if self.ps == 0:
            self.psb = v
            self.ps += 1
        elif self.ps == 1:
            self.psb += (v*256)
            self.ps = 0
            self.port = self.psb

    def status(self):       # 0=未接続 1=接続中 2=切断された
        c = self._c()
        if c is None:
            return 0
        return 2 if c.closed else 1


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
            self.ls.listen(16)
            self.ls.setblocking(False)
        except OSError:
            self.ls.close()
            self.ls = None

    def accepting(self):                # IN: 1=客が来た 0=まだ
        if self.ls is None:
            return 0
        while True:
            try:
                conn, addr = self.ls.accept()
            except BlockingIOError:
                break
            except OSError:
                break
            conn.setblocking(False)
            c = Connect()
            c.s = conn
            self.conns.append(c)
            if self.cur is None:
                self.cur = 0
        return 1 if self.conns else 0               # 以降は rx / send などがそのまま使える

    def listen_stop(self, v):
        if self.ls:
            self.ls.close()
            self.ls = None

    def reset(self,v):
        for c in self.conns:
            try:
                c.s.close()
            except OSError:
                pass
        self.conns = []
        self.cur = None
        if self.ls:
            try: self.ls.close()
            except OSError: pass
        self.ls = None
        self.name = ""
        self.port = 5000
        self.ps = 0
        self.psb = 0
        self.waitport = []

    def timer(self,v):
        self.t=v
        
    def count(self):                    # IN: 今の接続人数
        return len(self.conns) & 0xFF

    def select(self, v):                # OUT: 何番目の人を選ぶか
        self.cur = v if v < len(self.conns) else None