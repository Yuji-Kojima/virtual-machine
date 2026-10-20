def out_number(value):
    print(value)

def out_char(value):
    print(chr(value), end="")

ports={
    0 : (None,out_number),
    1 : (None,out_char)
}