import sys
from VM import VM,VMError
from formats import *

def load_file(path):
    with open(path, "rb") as f:
        data = f.read()
    
    if len(data) < HEADER_SIZE or data[:len(MAGIC)] != MAGIC:
        raise VMError("ヘッダーが不正")
    p = len(MAGIC)
    if data[p] != VERSION:
        print(f"バージョンが違います: {data[p]}")
        a = input("実行しますか(y/n)")
        if a == "y" or a == "Y":
            pass
        else:
            return
    load  = data[p + 1] + data[p + 2] * 256    # ロード先(下位が先)
    entry = data[p + 3] + data[p + 4] * 256    # 開始番地
    body = data[HEADER_SIZE:]
    if load + len(body) > 0x10000:
        raise VMError("メモリに収まりません")
    #print(len(data), data[:13].hex(" "))
    #print("load=", hex(load), "entry=", hex(entry), "body=", body.hex(" "))
    return load, entry, body

    


def main():
    if len(sys.argv) < 2:
        print("使い方: python main.py ファイル.sema3")
        return
    try:
        load, entry, body = load_file(sys.argv[1])
        vm = VM(body, load, entry)
        vm.run(debug=False)
    except VMError as e:
        print(f"\nVMエラー: {e}")

if __name__ == "__main__":
    main()