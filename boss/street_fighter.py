import pygame
from demiurge import Fighter
pygame.init()
screen_width=1000
screen_height=700
screen=pygame.display.set_mode((screen_width,screen_height))
clock=pygame.time.Clock()
RED=(255,0,0)
YELLOW=(255,255,0)
WHITE=(255,255,255)
warrior_size=162
warrior_scale=4
warrior_offset=[72,56]
warrior_data=[warrior_size,warrior_scale,warrior_offset]
demiurge_size=250
demiurge_scale=3
demiurge_offset=[112,107]
demiurge_data=[demiurge_size,demiurge_scale,demiurge_offset]
bg=pygame.image.load("images.jpg").convert_alpha()
bg=pygame.transform.scale(bg,(screen_width,screen_height))
warrior_sheet=pygame.image.load("./brawler_images/images/warrior/Sprites/warrior.png").convert_alpha()
demiurge_sheet=pygame.image.load("./brawler_images/images/wizard/Sprites/wizard.png").convert_alpha()
warrior_animation_steps=[10,8,1,7,7,3,7]
demiurge_animation_steps=[8,8,1,8,8,3,7]

def draw_bg():
    screen.blit(bg,(0,0))
def draw_health(screen,health,x,y):
    ratio=health/100
    pygame.draw.rect(screen,WHITE,(x-2,y-2,404,34))
    pygame.draw.rect(screen,RED,(x,y,400,30))
    pygame.draw.rect(screen,YELLOW,(x,y,400*ratio,30))
demiurge=Fighter(200,310,demiurge_data,demiurge_sheet,demiurge_animation_steps)
player=Fighter(700,310,warrior_data,warrior_sheet,warrior_animation_steps) #for now
running=True
while running:
    clock.tick(60) 
    draw_bg() 
    draw_health(screen,player.health,20,20)
    draw_health(screen,demiurge.health,500,20)
    player.move(screen_width,screen_height,screen,demiurge) 
    demiurge.move(screen_width,screen_height,screen,player,False)
    demiurge.ai_behavior(screen,player) 
    demiurge.draw(screen)
    player.update()
    demiurge.update() 
    player.draw(screen) 
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    pygame.display.update()
pygame.quit()
