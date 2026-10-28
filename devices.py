import msvcrt
import os
import display

def out_number(value):
    print(value)

def out_char(value):
    print(chr(value), end="",flush=True)

def run_display(value):
    display.D.start()

def kill_display(value):
    display.D.kill()



def in_char():
    value_raw = input("入力待ち")
    value = ord(value_raw[0]) if value_raw else 0
    return value

def in_key():
    key = msvcrt.getch()
    if key in (b"\x00", b"\xe0"):
        return msvcrt.getch()[0] | 0x100

    return key[0]


class FileDev:
    def __init__(self):
        self.name = bytearray()   # ファイル名を貯める入れ物
        self.data = None          # 開いたファイルの中身(失敗なら None)
        self.pos = 0              # 次に返すバイトの位置

    def out_name(self, v):
        if v == 0:                # 0 = 名前の終わり → open
            name = os.path.basename(bytes(self.name).decode(errors="ignore"))
            self.name.clear()
            self.pos = 0
            try:
                with open(os.path.join("data", name), "rb") as f:
                    self.data = f.read()
            except OSError:
                self.data = None
        else:
            self.name.append(v)

    def in_status(self):
        if self.data is None:
            return 2              # ファイルなし
        return 1 if self.pos >= len(self.data) else 0   # 1=EOF, 0=読める

    def in_byte(self):
        if self.data is None or self.pos >= len(self.data):
            return 0
        b = self.data[self.pos]
        self.pos += 1
        return b

F = FileDev()


ports={
    0 : (None,out_number),
    1 : (in_char,out_char),
    2 : (in_key,None,),
    3 : (None, run_display),
    4 : (None, kill_display),
    5 : (None, F.out_name),
    6 : (F.in_byte, None),
    7 : (F.in_status, None),
}