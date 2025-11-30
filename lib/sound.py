import pygame

def play_sound (name, volume=1.0):
    sound = pygame.mixer.Sound(f"./assets/sounds/{name}.mp3")
    sound.set_volume(volume)
    sound.play()
    
def play_music (name, volume=1.0, loop=0):
    pygame.mixer.music.load(f"./assets/music/{name}.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)

def stop_music():
    pygame.mixer.music.stop()
