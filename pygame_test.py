import pygame

SIZE = 128
SCALE = 4

# VM のメモリの代わり。1ピクセル1バイト、値は 0〜3
vram = bytearray(SIZE * SIZE)

# 適当にドットを書く(VM が STOREM でやることと同じ)
vram[0] = 3                          # 左上 (0, 0) を白
vram[5 * SIZE + 10] = 2              # (10, 5) を灰色
for x in range(SIZE):
    vram[64 * SIZE + x] = 1          # y=64 の行を濃い灰色の線にする

pygame.init()
screen = pygame.display.set_mode((SIZE * SCALE, SIZE * SCALE))

small = pygame.Surface((SIZE, SIZE), depth=8)
small.set_palette([(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)])

clock = pygame.time.Clock()
running = True
oh=4096
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:          # キーが押された瞬間
            if e.key == pygame.K_LEFT:
                print("左")
                oh -=1
            elif e.key == pygame.K_RIGHT:
                print("右")
                oh +=1
            elif e.key == pygame.K_UP:
                print("上")
                oh-=128
            elif e.key == pygame.K_DOWN:
                print("下")
                oh+=128
    vram[oh] = 3
    small.get_buffer().write(bytes(vram))                                   # VRAM を small に一括で書く
    screen.blit(pygame.transform.scale(small, screen.get_size()), (0, 0))   # 拡大して貼る
    pygame.display.flip()                                                   # 見せる
    clock.tick(60)

pygame.quit()