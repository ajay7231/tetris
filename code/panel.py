import pygame

class Panel:
   def __init__(self, surface_width,surface_height) -> None:
      self.surface = pygame.Surface((surface_width, surface_height))
      self.display_surface = pygame.display.get_surface()
      self.rect = self.surface.get_rect()

   def run(self):
      self.display_surface.blit(self.surface, self.rect)
      
   