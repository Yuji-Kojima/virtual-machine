import pygame
class Display():
    def __init__(self):
        
        self.SCALE = 4
        self.size = 128
        self.screen = None
        self.active = False

    def main(self, memory):
        self.memory = memory
        if self.active:
            print("すでにディスプレイが起動しています")
            return
        pygame.init()
        self.screen = pygame.display.set_mode((self.size*self.SCALE, self.size*self.SCALE))
        self.active = True

    def update(self):
        if not self.active:
            print("ディスプレイが起動していません")
            return

        

        pygame.display.flip()
    
    def kill(self):
        if not self.active:
            print("ディスプレイが起動していません")
            return
        pygame.quit()

D = Display()