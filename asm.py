from opcodes import *
from formats import *
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
    "JMPI" :  (JMPI,   "rr"),
    "DEC":   (DEC,   "r"),
    "PUSH":  (PUSH,  "r"),
    "POP":   (POP,   "r"),
    "JC":    (JC,    "a"),
    "JNC":   (JNC,   "a"),
    "MOVM":  (MOVM,  "aa"),
    "ADDR":  (ADDR,  "rr"),
    "SUBR":  (SUBR,  "rr"),
    "CMPR":  (CMPR,  "rr"),
    "AND":   (AND, "rn"),
    "OR":    (OR,  "rn"),
    "XOR":   (XOR, "rn"),
    "NOT":   (NOT, "r"),
    "SHL":   (SHL, "r"),
    "SHR":   (SHR, "r"),
    "MIAO":  (MIAO,  ""),
    "LOADLH":  (LOADLH,  "rrnn"),
    "CALZ":    (CALZ,    "a"),
    "CALNZ":    (CALNZ,    "a"),
    
    "DUMP":  (DUMP,  "aa"),
    
    "HALT":   (HALT,   ""),
}
regs={"A":0,"B":1,"C":2,"D":3}

SIZE = {"r": 1, "n": 1, "a": 2}




def encode_operand(kind, tok, labels):
    if kind == "r":
        tok=tok.upper()
        if tok not in regs:
            raise ValueError(f"未知のレジスタ: {tok}")
        return bytes([regs[tok]])
    elif kind == "n":
        return bytes([int(tok, 0) & 0xFF])
    elif kind == "a":
        if tok in labels:
            addr = labels[tok]
        else:
            try:
                addr = int(tok, 0)
            except ValueError:
                raise ValueError(f"未定義のラベル: {tok}")
        return bytes([addr & 0xFF, addr >> 8])
        
    
def parse_line(line):
    line = line.split(";")[0].strip()
    label = None
    if ":" in line:
        label, line = line.split(":", 1)
        label = label.strip()
        line = line.strip()
    if not line:
        return label, None, []
    parts = line.replace(",", " ").split()
    return label, parts[0].upper(), parts[1:]   # upperは大文字にするコード、[1:]は[0,1,2]の1以降を取り出す

def length(op):
    if op not in SPEC:
        raise ValueError(f"未知の命令: {op}")
    total = 1
    for k in SPEC[op][1]:
        total += SIZE[k]
    return total

def collect_labels(source, base):
    labels = {}
    addr = base
    org = base 
    for line in source.splitlines():
        label, op, args = parse_line(line)
        if op == ".ORG":
            addr = int(args[0], 0)
            org = addr
            continue
            
        if label:
            if label in labels:
                raise ValueError(f"ラベルが重複: {label}")
            labels[label] = addr
        if op:
            addr += length(op)
    return labels, org

def assemble(source, base=0):
    labels, org = collect_labels(source, base)
    load = bytes([org & 0xFF, org >> 8])
    entry = labels.get("start", org)                     # ← ここが start の部分
    entry_bytes = bytes([entry & 0xFF, entry >> 8])
    header = MAGIC + bytes([VERSION]) + load + entry_bytes
    
    out = bytearray()
    for line in source.splitlines():    # 1行ずつ取り出す
        _, op, args = parse_line(line)
        if op is None or op == ".ORG":
            continue     
        if op not in SPEC:
            raise ValueError(f"未知の命令: {op}")
        
        opcode, kinds = SPEC[op] 
        if len(args) != len(kinds):
            raise ValueError(f"{op}: オペランドは{len(kinds)}個必要です")
        out.append(opcode)        
        for kind, tok in zip(kinds, args):
            out += encode_operand(kind, tok, labels)   # オペランドを順に入れる
    return header + bytes(out)


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