data = bytes([
    # ループ(6番地)
    0x0B, 2, 0,           #  6: IN 2, A        キーを待たずに読む
    0x12, 0, 0,           #  9: CMP A, 0
    0x0E, 6, 0,           # 12: JZ 6           押されていなければ6番地へ
    0x0C, 1, 0,           # 15: OUT 1, A       文字を表示
    0x17, 0, 2, 3,        # 18: STOREI A, [lo=C, hi=D]  メモリへ保存
    0x08, 2,              # 22: INC C          番地を1つ進める
    0x12, 0, 0x0D,        # 24: CMP A, 13      Enterか?
    0x0F, 6, 0,           # 27: JNZ 6          Enterでなければ6番地へ

    # 終了処理
    0xFE, 0x00, 0x80, 0x20, 0x80,   # 30: DUMP 0x8000, 0x8020
    0x14,                 # 35: RET
])

name="keyboard_sub_routine_2.sema3"
with open(f"data/{name}", "wb") as f:
    f.write(data)
print(f"完了！ python main.py data/{name}")