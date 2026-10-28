from ram import memory
import threading
import pygame

class Display():
    SCALE = 4
    SIZE = 128
    VRAM = 0xA000       
    FPS = 60
    def __init__(self):
        self.active = False
        self.thread = None
        self.running=False
    def start(self):   
        if self.active:
            return
        self.active = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()


    def kill(self):                       
        self.active = False
        self.running=False
        pygame.quit()
                      

    def _loop(self): 
        pygame.init()
        size = self.SIZE * self.SCALE               
        screen = pygame.display.set_mode((size, size))
        
        small = pygame.Surface((self.SIZE, self.SIZE), depth=8)
        small.set_palette([((i >> 5) * 255 // 7,
                    ((i >> 2) & 7) * 255 // 7,
                    (i & 3) * 255 // 3) for i in range(256)])
        pygame.transform.scale(small, (size, size))
        clock = pygame.time.Clock()
        self.running=True
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.kill()
            data = bytes(memory[self.VRAM:self.VRAM + self.SIZE * self.SIZE])   # 毎フレーム読む        
            small.get_buffer().write(bytes(data))                                   # VRAM を small に一括で書く
            screen.blit(pygame.transform.scale(small, screen.get_size()), (0, 0))   # 拡大して貼る
            pygame.display.flip()                                                   # 見せる
            clock.tick(60)
D = Display()