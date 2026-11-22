import sys
import subprocess
import platform

def copy_to_clipboard(text):
    os_name = platform.system()
    if os_name == "Windows":
        subprocess.run(["clip"], input=text.encode("cp932"), check=True)
    elif os_name == "Darwin":  # Mac
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    else:  # Linux (xclipが必要)
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True)

def main():
    reg = "A"
    out = "0x01"
    space = "    "
    oh = True
    # コマンドライン引数が指定されていればそれを使い、なければ input() で受け取る
    if len(sys.argv) > 1:
        a = sys.argv[1]
    else:
        a = input("入力したい文字: ")
    if len(sys.argv) > 2:
        b = str(sys.argv[2])
        if b == "A" or b =="0":
            reg = "A"
        if b == "B" or b =="1":
            reg = "B"
        if b == "C" or b =="2":
            reg = "C"
        if b == "D" or b =="3":
            reg = "D"
    if len(sys.argv) > 3:
        c = str(sys.argv[3])
        out = c
    if len(sys.argv) > 4:
        space = ""
        d = int(sys.argv[4])
        space = " " * d
    if len(sys.argv) > 5:
        oh = False
            

    lines = []
    for i in a:
        lines.append(f"{space}LOAD {reg},{hex(ord(i))} ;{i}")
        lines.append(f"{space}OUT {out},{reg}")
    if oh == True:
        lines.append(f"{space}LOAD {reg},0x0A ;\\n")
        lines.append(f"{space}OUT {out},{reg}")        
    result = "\n".join(lines)
    copy_to_clipboard(result)
    print(result)
    print("\n--- クリップボードにコピーしました ---")

if __name__ == "__main__":
    main()