import sys
from settings import *
import pygame
from game import Game
from score import Score
from preview import Preview
from random import choice
from os.path import join


class Main:
   def __init__(self) -> None: 
      pygame.init()
      self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
      pygame.display.set_caption('Tetris')
      self.clock = pygame.time.Clock()

      #components
      self.next_shapes = [
       choice(list(TETROMINOS.keys())) for _ in range(3)
      ]


      self.game = Game(self.get_next_shape, self.update_score)
      self.score = Score()
      self.preview = Preview(self.next_shapes)

      self.music = pygame.mixer.Sound(join('sound','music.wav'))
      self.music.set_volume(0.1)
      self.music.play(-1)


   def update_score(self, lines, score, level):
      self.score.lines = lines
      self.score.score = score
      self.score.level = level

   def get_next_shape(self):
      next_shape = self.next_shapes.pop(0)
      self.next_shapes.append(choice(list(TETROMINOS.keys())))
      print(self.next_shapes)
      return next_shape
   
   def run(self):
      while True:
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               pygame.quit() 
               sys.exit() 
         self.display_surface.fill(GRAY)
         self.game.run()
         self.score.run()
         self.preview.run(self.next_shapes)
         self.game.draw_grid()

         pygame.display.update()
         self.clock.tick()

if __name__ == '__main__':
   main = Main()
   main.run()

