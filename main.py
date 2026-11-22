from VM import VM, VMError
import sys

def main():

    d = False
    if len(sys.argv) > 1:
        a = str(sys.argv[1])
        if a == "d":
            d = True
    else:
        pass
    try:
        vm = VM(b"", 0, 0)      # クラスから VM を1つ作る
        vm.run(debug=d)     # 0番地から実行を始める
    except VMError as e:
        print(f"\nVMエラー: {e}")

if __name__ == "__main__":
    main()