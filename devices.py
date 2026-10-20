import msvcrt

def out_number(value):
    print(value)

def out_char(value):
    print(chr(value), end="",flush=True)

def in_char():
    value_raw = input("入力待ち")
    value = ord(value_raw[0]) if value_raw else 0
    return value

def in_key():
    key = msvcrt.getch()
    if key in (b"\x00", b"\xe0"):
        return msvcrt.getch()[0] | 0x100

    return key[0]


ports={
    0 : (None,out_number),
    1 : (in_char,out_char),
    2 : (in_key,None,)
}