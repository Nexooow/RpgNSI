
import pygame

class Fighter:
    def __init__(self, x, y, data, sprite, animation, hitbox_height=180):
        self.flip = False
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.animation_list = self.load_frames(sprite, animation)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(
            (x, y, self.size/8*self.image_scale, hitbox_height))
        self.bubble = pygame.image.load('./assets/sprites/blocking.png')
        self.x = x
        self.y = y
        self.running = False
        self.jump = False
        self.gravity = 2
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.alive = True
        self.hit = False
        self.blocking = False
        self.health = 100
        self.dash_cooldown=0
        self.dash=False
        self.radiuspx = min(self.rect.width, self.rect.height)*9//2

    def load_frames(self, sprite, animation):
        animation_list = []
        for y, anim in enumerate(animation):
            temp_img_list = []
            for i in range(anim):
                temp_img = sprite.subsurface(
                    i*self.size, y*self.size, self.size, self.size)
                temp_img = pygame.transform.scale(
                    temp_img, (self.size*self.image_scale, self.size*self.image_scale))
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, allow_input=True):
        speed = 10
        dx = 0
        dy = 0
        self.running = False
        self.blocking = False
        if self.dash_cooldown==0:
            self.dash=False
        key = pygame.key.get_pressed()
        if allow_input and self.alive:
            if not self.attacking:
                if key[pygame.K_LEFT]:
                    self.flip = True
                if key[pygame.K_RIGHT]:
                    self.flip = False
                
                if key[pygame.K_a]:
                    self.blocking = True
                if key[pygame.K_e] and self.dash_cooldwon==0:
                    self.dash=True
                    dx= dx-speed*30 if self.flip else dx+speed*30
                    self.dash_cooldown=300
                else:
                    if self.dash:
                        self.dash_cooldown-=1
                    if key[pygame.K_q]:
                        dx -= speed
                        self.running = True
                        # self.flip=True
                    elif key[pygame.K_d]:
                        dx += speed
                        self.running = True
                        # self.flip=False
                    elif key[pygame.K_z] and self.jump == False:
                        self.y = -30
                        self.jump = True
                    elif key[pygame.K_s] and self.jump:
                        self.y += 10
                    elif key[pygame.K_r] or key[pygame.K_t]:
                        self.attack(surface, target)
                        if key[pygame.K_r]:
                            self.attack_type = 1
                        if key[pygame.K_t]:
                            self.attack_type = 2
        self.y += self.gravity
        dy += self.y
        if self.rect.left+dx < 0:
            dx = -self.rect.left
        if self.rect.right+dx > screen_width:
            dx = screen_width-self.rect.right
        if self.rect.bottom+dy > screen_height-110:
            self.y = 0
            self.jump = False
            dy = screen_height-110-self.rect.bottom
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)
        elif self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)
        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks()-self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def ai_behavior(self, surface, player):
        if self.alive and player.alive:
            if self.attack_cooldown == 0:
                self.flip = player.rect.x < self.rect.x
                distance = abs(player.rect.x - self.rect.x)
                if distance > 150:
                    if player.rect.x < self.rect.x:
                        self.rect.x -= 5
                        self.running = True
                        self.flip = True
                    elif player.rect.x > self.rect.x:
                        self.rect.x += 5
                        self.running = True
                        self.flip = False
                else:
                    attack_choice = [1, 2]
                    self.attack_type = attack_choice[pygame.time.get_ticks(
                    ) % 2]
                    self.attack(surface, player)
                    self.attack_cooldown = 20
            else:
                self.attack_cooldown -= 1

    def attack(self, surface, target=None):
        self.attacking = True
        attacking_rect = pygame.Rect(
            self.rect.centerx-(2*self.rect.width*self.flip), self.rect.y, 2*self.rect.width, self.rect.height)
        if target is not None:
            if attacking_rect.colliderect(target.rect):
                if not target.blocking or (target.flip and self.flip) or (not target.flip and not self.flip):
                    target.health -= 10
        pygame.draw.rect(surface, (0, 255, 0), attacking_rect)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        if self.blocking:

            self.bubble = pygame.transform.scale(
                self.bubble, (self.size*self.image_scale, self.size*self.image_scale))
            self.image = self.bubble
        img = pygame.transform.flip(self.image, self.flip, False)
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
        surface.blit(
            img, (self.rect.x-(self.offset[0]*self.image_scale), self.rect.y-(self.offset[1]*self.image_scale)))
