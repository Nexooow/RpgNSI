import networkx as nx
import matplotlib.pyplot as plt
import base64
import numpy as np
import pygame
from io import BytesIO
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
from matplotlib.transforms import offset_copy
from random import randint,choice
from meteor import *
from boom import *
from text_display import *
from classe_graphe import *
from sound import *
from npc import *
def display_frames(image,frame_width,frame_height):
    frames=[]
    sheet_width=image.get_width()
    sheet_height=image.get_height()
    num_frames=sheet_width//frame_width
    for i in range(num_frames):
        frame=image.subsurface((i*frame_width,0,frame_width,frame_height))
        frames.append(frame)
    return frames
graphe=Graph([("Auberge","Mountain",47),("Auberge","Dawn of the world",21),("Dawn of the world","Auberge",21),("Mountain","Ceilidh",36),("Mountain","Auberge",47),("Ceilidh","Mountain",36),("Ceilidh","Auberge",31),("Auberge","Elder Tree",21),("Auberge","Ceilidh",36)],["Auberge","Mountain","Ceilidh","Dawn of the world","Elder Tree"],True)
with open("main_map.txt","r") as f0:
    b64=f0.read()
with open("mountain_map.txt","r") as f1:
    b64_mountain=f1.read()
with open("caelid_map.txt","r") as f2:
    b64_cailidh=f2.read()
with open("radahn_chibi.txt","r") as f3:
    b64_rad=f3.read()
with open("hand_img.txt","r") as f4:
    b64_hand=f4.read()
with open("castle_img.txt",'r') as f5:
    b64_c=f5.read()
with open("oz_img.txt","r") as f6:
    b64_oz=f6.read()
with open("feet_img.txt","r") as f7:
    b64_feet=f7.read()
with open("radahn_fight_zone.txt","r") as f8:
    b64_rad_zone=f8.read()
with open("radahn_pixel.txt","r") as f9:
    b64_radahn=f9.read()
bigfoot=NPC("Casan famhair",(200,400))
giant=NPC("Oz",(500,200))
radahn=NPC("Radahn, Consort of Joy",(766,350))
castle=NPC("Old Castle",(640,570))
finger=NPC("The Toucher",(650,150))
nodes_icons={radahn.name:(b64_rad,'jpeg'),finger.name:(b64_hand,'jpeg'),castle.name:(b64_c,'jpeg'),giant.name:(b64_oz,'webp'),bigfoot.name:(b64_feet,'png')}
graphe_mt=Graph([(bigfoot.name,giant.name,5),(giant.name,bigfoot.name,5)],[bigfoot.name,giant.name],True)
graphe_caelid=Graph([(radahn.name,castle.name,2),(castle.name,finger.name,6),(finger.name, castle.name,5),(castle.name,radahn.name,1)],[castle.name,radahn.name,finger.name],True)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1000, 700))
background = graphe.affichage_graphe(b64,{"Auberge": (200, 400), "Mountain": (600, 120),"Ceilidh": (660, 480),"Dawn of the world": (450, 500),"Elder Tree": (500, 230)},'webp',nodes_icons)
screen.blit(background,(0,0))
running = True
main_img=background
caelid=None
mt=None
fight_zone=None
list_meteor=[]
clock=pygame.time.Clock()
half_radahn=pygame.image.load(BytesIO(base64.b64decode(b64_radahn))).convert_alpha()
radahn_frames=display_frames(half_radahn,1200,1350)
radahn_frame_index=0
explosion_group=pygame.sprite.Group()
start_ticks=pygame.time.get_ticks()
font = pygame.font.SysFont('Cinzel Decorative', 30)
music_playing=False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type==pygame.MOUSEBUTTONUP:
            position=event.pos
            if main_img==background and pygame.Rect(500,0,500,350).collidepoint(position):
                mt=graphe_mt.affichage_graphe(b64_mountain,{bigfoot.name:bigfoot.location,giant.name:giant.location},'webp',nodes_icons)
                main_img=mt
            if main_img==background and pygame.Rect(500,400,300,200).collidepoint(position):
                caelid=graphe_caelid.affichage_graphe(b64_cailidh,{radahn.name:radahn.location,castle.name:castle.location,finger.name:finger.location},'webp',nodes_icons)
                main_img=caelid
            if main_img==caelid:
                if pygame.Rect(radahn.location[0]-100,radahn.location[1]-100,200,200).collidepoint(position):
                    fight_zone=pygame.image.load(BytesIO(base64.b64decode(b64_rad_zone))).convert()
                    main_img=fight_zone
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_o:
                main_img=background
    screen.blit(main_img,(0,0))
    if main_img==fight_zone:
        if not music_playing:
            play_music("/mnt/c/Users/peter/Downloads/Gloria_Gaynor_-_I_Will_Survive_Re-Recorded_Remastered_(SkySound.cc).mp3")
            music_playing=True
        seconds=(pygame.time.get_ticks()-start_ticks)/1000
        counter=int(195-seconds)
        text=str(counter).rjust(3) if counter>0 else ""
        if counter>0:
            stop_music()
        screen.blit(radahn_frames[radahn_frame_index],(0,-120))
        radahn_frame_index=(radahn_frame_index+1)%len(radahn_frames)
        this=randint(1,200)
        if len(list_meteor)<10 and this<=10:
            if this>3:
                list_meteor.append(Meteor((randint(25,910),-25)))
            else:
                border=choice([25,910])
                list_meteor.append(Meteor((border,randint(-25,150))))
        for meteor in list_meteor:
            meteor.deplace()
            meteor.frame_index=(meteor.frame_index+1)%len(meteor.frames)
            if meteor.rect.bottom>=480:
                list_meteor.remove(meteor)
                explosion=Explosion(meteor.rect.center[0],meteor.rect.center[1],meteor.size)
                explosion_group.add(explosion)
            else:
                screen.blit(meteor.frame,meteor.rect)
        text_render_centered_up(screen,"Survive","bold",color=(255,0,0),pos=(500,100))
        screen.blit(font.render(text,True,(255,0,0)),(500,150))
    clock.tick(45)
    explosion_group.draw(screen)
    explosion_group.update()

    pygame.display.update()
pygame.quit()
print(graphe.paths("Ceilidh","Elder Tree"))
