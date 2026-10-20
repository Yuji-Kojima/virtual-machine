
data = bytes([
0x0B,2,0,#ポート2、Aレジスタにキー入力を代入
0x12,0,0,#ゼロを引いて答えがゼロかチェック
0x0E,0,0,#zでアドレス0000にジャンプ(ループ)
0x0C,1,0,#ポート1,AレジスタのASCII文字を出力
0x08,1, #Bレジスタの値を+1
0x05,1,0x14,0, #0x14番地にBレジスタの内容を書き込む
0x05,0,0,0x01, #0100~番地にAレジスタの内容を書き込む
0x12,0,0x0D,#0x0Dを引いて答えがゼロかチェック
0x0F,0,0,#zでなければアドレス0000にジャンプ(ループ)
0xFE,0,0,0xFF,0x01,#0000~01FFまでをprint
0x14 #RET
])

name="keyboard_sub_routine.sema3"
with open(f"data/{name}", "wb") as f:
    f.write(data)
print(f"完了！ python main.py data/{name}")