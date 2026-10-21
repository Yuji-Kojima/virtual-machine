from opcodes import *
import sys

# r = レジスタ, n = 1バイト数値, a = 16bit番地(ラベル可)
SPEC = {
    "NOP":    (NOP,    ""),
    "LOAD":   (LOAD,   "rn"),
    "ADD":    (ADD,    "rn"),
    "SUB":    (SUB,    "rn"),
    "LOADM":  (LOADM,  "ra"),
    "STOREM": (STOREM, "ra"),
    "MOV":    (MOV,    "rr"),
    "INC":    (INC,    "r"),
    "IN":     (IN,     "nr"),
    "OUT":    (OUT,    "nr"),
    "JMP":    (JMP,    "a"),
    "JZ":     (JZ,     "a"),
    "JNZ":    (JNZ,    "a"),
    "CALL":   (CALL,   "a"),
    "RET":    (RET,    ""),
    "CMP":    (CMP,    "rn"),
    "STOREI": (STOREI, "rrr"),
    "LOADI":  (LOADI,  "rrr"),
    "JMPI" :  (JMPI,   "a"),

    "DEC":   (DEC,   "r"),
    "PUSH":  (PUSH,  "r"),
    "POP":   (POP,   "r"),
    "JC":    (JC,    "a"),
    "JNC":   (JNC,   "a"),
    "MOVM":  (MOVM,  "aa"),
    "DUMP":  (DUMP,  "aa"),
    "MIAO":  (MIAO,  ""),
    "HALT":   (HALT,   ""),
}
regs={"A":0,"B":1,"C":2,"D":3}
def encode_operand(kind, tok):
    if kind == "r":
        tok=tok.upper()
        if tok not in regs:
            raise ValueError(f"未知のレジスタ: {tok}")
        return bytes([regs[tok]])
    elif kind == "n":
        return bytes([int(tok, 0) & 0xFF])
    elif kind == "a":
        addr = int(tok, 0)
        return bytes([addr & 0xFF, addr >> 8])
        
    


def assemble(source):
    out = bytearray()
    for line in source.splitlines():    # 1行ずつ取り出す
        line = line.split(";")[0].strip()
        if not line:
            continue
        parts = line.replace(",", " ").split() 
        op, args = parts[0].upper(), parts[1:] # upperは大文字にするコード、[1:]は[0,1,2]の1以降を取り出す
        if op not in SPEC:
            raise ValueError(f"未知の命令: {op}")
        opcode, kinds = SPEC[op] 
        out.append(opcode)
        if len(args) != len(kinds):
            raise ValueError(f"{op}: オペランドは{len(kinds)}個必要です")
        for kind, tok in zip(kinds, args):
            out += encode_operand(kind, tok)   # オペランドを順に入れる
    return bytes(out)


def main():
    if len(sys.argv) < 3:
        print("asm.py ソースファイル名.sasm 出力先名.sema3")
        return
    with open(sys.argv[1], encoding="utf-8") as f:
        source = f.read()
    program = assemble(source) # ここで変換
    with open(sys.argv[2], "wb") as f:
        f.write(program)
    print(f"完了: {sys.argv[2]} ({len(program)}バイト)")


if __name__ == "__main__":
    main()