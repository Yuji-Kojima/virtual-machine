## アセンブラ(asm.py)

`.sasm`(アセンブリのソース)を `.sema3`(実行ファイル)に変換します。ヘッダー13バイトは自動で付きます。

```
python asm.py ソース.sasm 出力.sema3
```

例:

```
python asm.py hello.sasm data/hello.sema3
```

### 書き方

- 1行に1命令。`;` から行末まではコメント
- ラベルは `名前:` と書く。`JMP` や `CALL` の飛び先に使える
- `.ORG 0x2000` でロード位置を指定する(省略すると 0)
- `start:` というラベルがあれば、そこから実行を始める(なければ `.ORG` の位置)
- 数値は10進か `0x` 付きの16進。レジスタは `A`〜`D`

### 例(`H` を表示して OS に戻る)

```
.ORG 0x2000
start:
    LOAD A, 72      ; 'H'
    OUT 1, A        ; 1文字表示
    LOAD A, 10      ; 改行
    OUT 1, A
    RET             ; OS に戻る
```

`data/` に置いたら、`python main.py` で OS を起動して、`file` と打ってから `hello.sema3` と打つと実行できます。プログラムは `RET` で終えてください(`HALT` だと VM ごと止まります)。
