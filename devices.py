import msvcrt
import os
import display
import time
import ctypes

try:
    import sound          # 音源(sounddevice が無ければ音なしで動く)
except Exception:
    sound = None

gas = ctypes.windll.user32.GetAsyncKeyState

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
    if not msvcrt.kbhit():
        return 0              # 押されていなければ 0 を返して、すぐ戻る
    key = msvcrt.getch()
    if key in (b"\x00", b"\xe0"):
        return msvcrt.getch()[0] | 0x100
    return key[0]

_next = time.perf_counter()

def wait_frames(n):
    global _next
    now = time.perf_counter()
    if _next < now:            # 遅れていたら、今を基準にやり直す
        _next = now
    #_next += n / 60            # n フレーム先を目標にする
    _next += 1 / 60            # 1 フレーム先を目標にする
    delay = _next - time.perf_counter()
    if delay > 0:
        time.sleep(delay)








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


KEYS = [0x53, 0x44, 0x46, 0x20, 0x4A, 0x4B, 0x4C, 0xA0]   # 初期値
_slot = 0

def read_held():
    pass
def read_edge():
    pass
def set_slot():
    pass
def set_key():
    pass

F = FileDev()

sel = 0
 
def snd_sel(v):
    global sel
    sel = v
 
def snd_val(v):
    if sound is None:
        return
    if sel == 0:
        sound.freq = 0.0 if v == 0 else 440 * 2 ** ((v - 69) / 12)
 

ports={
    0 : (None,out_number),
    1 : (in_char,out_char),
    2 : (in_key,None,),
    3 : (None, run_display),
    4 : (None, kill_display),
    5 : (None, F.out_name),
    6 : (F.in_byte, None),
    7 : (F.in_status, None),
    8 : (None, wait_frames),
    9 : (read_held, None),
    10: (read_edge, None),
    11: (None, set_slot),   # どのスロットを変えるか
    12: (None, set_key),    # そのスロットのキーコード
    13: (None, snd_sel),
    14: (None, snd_val),
}