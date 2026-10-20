import sys
from VM import VM,VMError

def load_file(path):
    with open(path, "rb") as f:
        return f.read()

def main():
    if len(sys.argv) < 2:
        print("ファイル名を入力してください")
        return
    vm = VM(load_file(sys.argv[1]))
    try:
        vm.run()
    except VMError as e:
        print(f"\nVMエラー: {e}")

if __name__ == "__main__":
    main()