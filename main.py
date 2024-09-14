import pygame
import random

import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
tracks = ["C:\\Users\\lucas\\Desktop\\pws\\simulatie\\track1.png"
        "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\2.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\2.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\3.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\4.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\5.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\6.png", 
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\7.png",
          "C:\\Users\\lucas\\Desktop\\pws\\simulatie\\8a.png"]

while running:
   
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    screen.blit(img, (0, 0))

    pygame.display.flip()

    clock.tick(60)  

pygame.quit()