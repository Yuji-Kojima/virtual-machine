import msvcrt
import display

class Updates():
    def __init__(self):
        self.f=[]
        self.memory=None
    def update(self):
        for i in self.f:
            i()

u=Updates()

def out_number(value):
    print(value)

def out_char(value):
    print(chr(value), end="",flush=True)

def out_bytes(value):
    print(chr(value & 0xFF), end="", flush=True)

def in_char():
    value_raw = input("入力待ち")
    value = ord(value_raw[0]) if value_raw else 0
    return value

def in_key():
    key = msvcrt.getch()
    if key in (b"\x00", b"\xe0"):
        return msvcrt.getch()[0] | 0x100

    return key[0]

def run_display():
    display.main(u.memory)
    u.f.append(display.update)

def kill_display():
    display.kill()
    if display.update in u.f:
        u.f.remove(display.update)

ports={
    0 : (None,out_number),
    1 : (in_char,out_char),
    2 : (in_key,None,),
    3 : (None, out_bytes),
    4 : (None, run_display),
    5 : (None, kill_display)
}