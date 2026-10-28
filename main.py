from VM import VM, VMError

def main():
    try:
        vm = VM(b"", 0, 0)      # クラスから VM を1つ作る
        vm.run(debug=False)     # 0番地から実行を始める
    except VMError as e:
        print(f"\nVMエラー: {e}")

if __name__ == "__main__":
    main()