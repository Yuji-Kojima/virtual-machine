"""semart お絵かきツール (pygame)

使い方:
  python semart_edit.py                         新規 16x16 (保存先 data/new.semart)
  python semart_edit.py data/hero.semart        あれば開く / なければ 16x16 で新規作成
  python semart_edit.py data/hero.semart --size 32x32

操作:
  左クリック         描く               右クリック  スポイト(その色を拾う)
  右のパレットをクリック  色を選ぶ (色の番号 = そのままバイトの値。RGB332)
  P 鉛筆   F 塗りつぶし   I スポイト   G グリッド表示
  Ctrl+S 保存   Ctrl+Z 元に戻す   Esc 終了(未保存なら2回押す)

形式: b"ART" + 縦(1バイト) + 横(1バイト) + ピクセル(1ピクセル1バイト、行ごとに続く)
"""
import argparse
import os
import sys

import pygame

MAGIC = b"ART"
CELL = 16          # パレット1マスの大きさ(px)
MAX_VIEW = 512     # キャンバスの表示の最大サイズ(px)


def rgb332(i):
    """バイト値 i (RRRGGGBB) を RGB にする。display.py のパレットと同じ式。"""
    return ((i >> 5) * 255 // 7, ((i >> 2) & 7) * 255 // 7, (i & 3) * 255 // 3)


PALETTE = [rgb332(i) for i in range(256)]


class Art:
    """絵のデータ本体(画面に依存しない部分)。"""

    def __init__(self, w, h, pixels=None):
        if not (1 <= w <= 255 and 1 <= h <= 255):
            raise ValueError("縦横は 1~255 にしてください")
        self.w, self.h = w, h
        self.px = bytearray(pixels) if pixels is not None else bytearray(w * h)
        if len(self.px) != w * h:
            raise ValueError("ピクセル数が 縦×横 と合いません")

    def get(self, x, y):
        return self.px[y * self.w + x]

    def set(self, x, y, c):
        self.px[y * self.w + x] = c

    def fill(self, x, y, c):
        """(x, y) とつながっている同じ色の範囲を c で塗る。"""
        old = self.get(x, y)
        if old == c:
            return
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if 0 <= cx < self.w and 0 <= cy < self.h and self.get(cx, cy) == old:
                self.set(cx, cy, c)
                stack += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]

    def to_bytes(self):
        return MAGIC + bytes([self.h, self.w]) + bytes(self.px)

    @staticmethod
    def from_bytes(data):
        if len(data) < 5 or data[:3] != MAGIC:
            raise ValueError("semart ファイルではありません(先頭が ART ではない)")
        h, w = data[3], data[4]
        body = data[5:]
        if len(body) != w * h:
            raise ValueError(f"サイズが合いません: {w}x{h} なのにピクセルが {len(body)} 個")
        return Art(w, h, body)


class App:
    def __init__(self, path, art):
        pygame.init()
        self.path, self.art = path, art
        self.tool = "pencil"
        self.color = 0xFF
        self.grid = True
        self.modified = False
        self.quit_armed = False
        self.undo = []
        self.drag = False
        self.last = None
        self.msg = ""

        self.scale = max(1, min(MAX_VIEW // art.w, MAX_VIEW // art.h))
        self.cw, self.ch = art.w * self.scale, art.h * self.scale
        m = 12
        self.cx, self.cy = m, m
        self.px0, self.py0 = self.cx + self.cw + m, m
        pal = 16 * CELL
        width = self.px0 + pal + m
        height = max(self.ch, pal + 70) + m * 2 + 30
        self.screen = pygame.display.set_mode((width, height))
        self.status_y = height - 26
        self.font = pygame.font.SysFont("meiryo,yugothic,msgothic,notosanscjkjp", 16)
        self.surf = pygame.Surface((art.w, art.h))
        self.redraw_all()
        self.update_title()

    # ---------- 表示まわり ----------
    def redraw_all(self):
        for y in range(self.art.h):
            for x in range(self.art.w):
                self.surf.set_at((x, y), PALETTE[self.art.get(x, y)])

    def update_title(self):
        pygame.display.set_caption(f"semart edit - {self.path}{' *' if self.modified else ''}")

    def canvas_pos(self, pos):
        x = (pos[0] - self.cx) // self.scale
        y = (pos[1] - self.cy) // self.scale
        if pos[0] >= self.cx and pos[1] >= self.cy and 0 <= x < self.art.w and 0 <= y < self.art.h:
            return int(x), int(y)
        return None

    def pal_index(self, pos):
        col, row = (pos[0] - self.px0) // CELL, (pos[1] - self.py0) // CELL
        if pos[0] >= self.px0 and pos[1] >= self.py0 and 0 <= col < 16 and 0 <= row < 16:
            return int(row * 16 + col)
        return None

    def draw(self):
        self.screen.fill((38, 38, 46))
        big = pygame.transform.scale(self.surf, (self.cw, self.ch))
        self.screen.blit(big, (self.cx, self.cy))
        if self.grid and self.scale >= 8:
            for i in range(self.art.w + 1):
                x = self.cx + i * self.scale
                pygame.draw.line(self.screen, (90, 90, 100), (x, self.cy), (x, self.cy + self.ch))
            for j in range(self.art.h + 1):
                y = self.cy + j * self.scale
                pygame.draw.line(self.screen, (90, 90, 100), (self.cx, y), (self.cx + self.cw, y))
        pygame.draw.rect(self.screen, (200, 200, 210), (self.cx - 1, self.cy - 1, self.cw + 2, self.ch + 2), 1)

        for i in range(256):
            r = pygame.Rect(self.px0 + (i % 16) * CELL, self.py0 + (i // 16) * CELL, CELL, CELL)
            pygame.draw.rect(self.screen, PALETTE[i], r)
        sel = pygame.Rect(self.px0 + (self.color % 16) * CELL, self.py0 + (self.color // 16) * CELL, CELL, CELL)
        pygame.draw.rect(self.screen, (255, 255, 255), sel, 2)
        pygame.draw.rect(self.screen, (0, 0, 0), sel.inflate(-4, -4), 1)

        sw_y = self.py0 + 16 * CELL + 10
        pygame.draw.rect(self.screen, PALETTE[self.color], (self.px0, sw_y, 40, 40))
        pygame.draw.rect(self.screen, (200, 200, 210), (self.px0, sw_y, 40, 40), 1)
        self.screen.blit(self.font.render(f"色 0x{self.color:02X}", True, (230, 230, 235)), (self.px0 + 48, sw_y))
        names = {"pencil": "鉛筆", "fill": "塗りつぶし", "pick": "スポイト"}
        self.screen.blit(self.font.render(names[self.tool], True, (230, 230, 235)), (self.px0 + 48, sw_y + 20))

        mx, my = pygame.mouse.get_pos()
        cp = self.canvas_pos((mx, my))
        hover = f"({cp[0]},{cp[1]})=0x{self.art.get(*cp):02X}  " if cp else ""
        text = f"{hover}{self.art.w}x{self.art.h}  {self.msg}"
        self.screen.blit(self.font.render(text, True, (230, 230, 235)), (12, self.status_y))

    # ---------- 編集 ----------
    def push_undo(self):
        self.undo.append(bytes(self.art.px))
        if len(self.undo) > 100:
            self.undo.pop(0)

    def put(self, x, y):
        if self.art.get(x, y) != self.color:
            self.art.set(x, y, self.color)
            self.surf.set_at((x, y), PALETTE[self.color])
            self.modified = True

    def line(self, a, b):
        (x0, y0), (x1, y1) = a, b
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.put(x0, y0)
            if (x0, y0) == (x1, y1):
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "wb") as f:
            f.write(self.art.to_bytes())
        self.modified = False
        self.msg = f"保存しました ({5 + len(self.art.px)}バイト)"
        if self.art.w > 128 or self.art.h > 128:
            self.msg += " ※画面は128x128です"
        print("完了:", self.path, self.msg)

    def handle(self, e):
        """イベントを1つ処理する。続けるなら True、終了なら False。"""
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.KEYDOWN:
            ctrl = e.mod & pygame.KMOD_CTRL
            if e.key != pygame.K_ESCAPE:
                self.quit_armed = False
            if ctrl and e.key == pygame.K_s:
                self.save()
            elif ctrl and e.key == pygame.K_z:
                if self.undo:
                    self.art.px = bytearray(self.undo.pop())
                    self.redraw_all()
                    self.modified = True
            elif e.key == pygame.K_p:
                self.tool = "pencil"
            elif e.key == pygame.K_f:
                self.tool = "fill"
            elif e.key == pygame.K_i:
                self.tool = "pick"
            elif e.key == pygame.K_g:
                self.grid = not self.grid
            elif e.key == pygame.K_ESCAPE:
                if self.modified and not self.quit_armed:
                    self.quit_armed = True
                    self.msg = "未保存です。Esc をもう一度で破棄して終了 (Ctrl+S で保存)"
                else:
                    return False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            idx = self.pal_index(e.pos)
            cp = self.canvas_pos(e.pos)
            if e.button == 1 and idx is not None:
                self.color = idx
            elif e.button == 1 and cp is not None:
                if self.tool == "pick":
                    self.color = self.art.get(*cp)
                elif self.tool == "fill":
                    self.push_undo()
                    self.art.fill(*cp, self.color)
                    self.redraw_all()
                    self.modified = True
                else:
                    self.push_undo()
                    self.drag, self.last = True, cp
                    self.put(*cp)
            elif e.button == 3 and cp is not None:
                self.color = self.art.get(*cp)
        elif e.type == pygame.MOUSEMOTION and self.drag:
            cp = self.canvas_pos(e.pos)
            if cp is not None:
                self.line(self.last, cp)
                self.last = cp
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.drag = False
        self.update_title()
        return True

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for e in pygame.event.get():
                if not self.handle(e):
                    running = False
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()


def main():
    ap = argparse.ArgumentParser(description="semart お絵かきツール")
    ap.add_argument("path", nargs="?", default="data/new.semart")
    ap.add_argument("--size", default="16x16", help="新規作成時の 横x縦 (例: 32x32)")
    args = ap.parse_args()

    try:
        if os.path.exists(args.path):
            with open(args.path, "rb") as f:
                art = Art.from_bytes(f.read())
        else:
            w, h = (int(v) for v in args.size.lower().split("x"))
            art = Art(w, h)
    except ValueError as err:
        print("エラー:", err)
        sys.exit(1)
    if art.w > 128 or art.h > 128:
        print("注意: 画面は 128x128 なので、これより大きい絵ははみ出します")
    App(args.path, art).run()


if __name__ == "__main__":
    main()
