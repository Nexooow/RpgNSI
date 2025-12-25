import pygame
class Fighter:
    def __init__(self,x,y,data,sprite,animation,attack_frame,hitbox_height=180):
        self.flip=False
        self.size=data[0]
        self.image_scale=data[1]
        self.offset=data[2]
        self.animation_list=self.load_frames(sprite,animation)
        self.action=0
        self.frame_index=0
        self.image=self.animation_list[self.action][self.frame_index]
        self.update_time=pygame.time.get_ticks()
        self.rect=pygame.Rect((x,y,self.size/8*self.image_scale,hitbox_height))
        self.bubble=pygame.image.load('blocking.png')
        self.x=x
        self.y=y
        self.running=False
        self.jump=False
        self.gravity=1.7
        self.attacking=False
        self.attack_type=0
        self.attack_cooldown=0
        self.alive=True
        self.hit=False
        self.blocking=False
        self.dash_cooldown=0
        self.dash=False
        self.health=100
        self.radiuspx=min(self.rect.width,self.rect.height)*9//2
        self.mask=pygame.mask.from_surface(self.image)
        self.img_pos=(self.rect.x-(self.offset[0]*self.image_scale),self.rect.y-(self.offset[1]*self.image_scale))
        self.has_hit=False
        self.attack_frame=attack_frame
        self.hit_count=0
        self.last_hit_time=0
        self.combo_window=1000
        self.angry=False
        self.anger_timer=0
        self.fireballs=[]
    def load_frames(self,sprite,animation):
        animation_list=[]
        for y,anim in enumerate(animation):
            temp_img_list=[]
            for i in range(anim):
                temp_img=sprite.subsurface(i*self.size,y*self.size,self.size,self.size)
                temp_img=pygame.transform.scale(temp_img,(self.size*self.image_scale,self.size*self.image_scale))
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list
    def move(self,screen_width,screen_height,surface,target,allow_input=True):
        speed=10
        dx=0
        dy=0
        self.running=False
        self.blocking=False
        if self.dash_cooldown==0:
            self.dash=False
        key=pygame.key.get_pressed()
        if allow_input and self.alive:
            if not self.attacking:
                
                if key[pygame.K_LEFT]:
                    self.flip=True
                if key[pygame.K_RIGHT]:
                    self.flip=False
                if key[pygame.K_a]:
                    self.blocking=True
                if key[pygame.K_e] and self.dash_cooldown==0:
                    dx= dx-speed*10 if self.flip else dx+speed*10
                    self.dash=True
                    self.dash_cooldown=300
                    
                    
                else:
                    if self.dash:
                        self.dash_cooldown-=1
                    
                    if not self.blocking:
                        if key[pygame.K_q]:
                            dx-=speed
                            self.running=True
                            
                        elif key[pygame.K_d]:
                            dx+=speed
                            self.running=True
                            
                        elif key[pygame.K_z] and self.jump==False:
                            self.y=-30
                            self.jump=True
                        elif key[pygame.K_s] and self.jump:
                            self.y+=10
                        elif key[pygame.K_r] or key[pygame.K_t]:
                            self.attack(surface,target)
                            if key[pygame.K_r]:
                                self.attack_type=1
                            if key[pygame.K_t]:
                                self.attack_type=2
        self.y+=self.gravity
        dy+=self.y
        if self.rect.left+dx<0:
            dx=-self.rect.left
        if self.rect.right+dx>screen_width:
            dx= screen_width-self.rect.right
        if self.rect.bottom+dy>screen_height-110:
            self.y=0
            self.jump=False
            dy=screen_height-110-self.rect.bottom
        self.rect.x+=dx
        self.rect.y+=dy
    def update(self,target=None):
        if self.health<=0:
            self.health=0
            self.alive=False
            self.update_action(6)
        elif self.hit:
            self.update_action(5)
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type==2:
                self.update_action(4)
        elif self.jump:
            self.update_action(2)
        elif self.running:
            self.update_action(1)
        else:
            self.update_action(0)
        animation_cooldown=50
        self.image=self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks()-self.update_time> animation_cooldown:
            self.frame_index+=1
            self.update_time=pygame.time.get_ticks()
        if self.frame_index>=len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index=len(self.animation_list[self.action])-1
            else:
                self.frame_index=0
                if self.action==3 or self.action==4:
                    self.attacking=False
                    self.attack_cooldown=20
                if self.action==5:
                    self.hit=False
                    self.attacking=False
                    self.attack_cooldown=20
        if self.attacking and not self.has_hit:
            if self.frame_index in self.attack_frame[self.attack_type]:
                self.apply_attack(target)
    def apply_attack(self,player):
        if player is None:
            return
        attacking_rect=pygame.Rect(self.rect.centerx-(2*self.rect.width*self.flip),self.rect.y,2*self.rect.width,self.rect.height)
        if attacking_rect.colliderect(player.rect):
                if not player.blocking or (player.flip and self.flip) or (not player.flip and not self.flip):
                    player.health-=10
                    player.hit=True
                    self.has_hit=True
    def ai_behavior(self,surface,player):
        if self.alive and player.alive:
            if player.has_hit:
                player.hit_count+=1
            if player.hit_count>=30 and not self.angry:
                    self.angry=True
                    if player.rect.x<=500:
                        self.rect.x=800
                    else:
                        self.rect.x=200
                    player.hit_count=0
                    return
            if self.angry:
                    if self.anger_timer%100==0:
                        self.fireballs.append(Fireball(self.rect.centerx,self.rect.centery,-1 if self.flip else 1,15,self.image_scale//2,pygame.image.load('./assets/sprites/fireball.png').convert_alpha()))   
                    self.anger_timer+=1
                    if self.anger_timer>=600:
                        self.angry=False
                        
                        self.anger_timer=0
                    for fireball in self.fireballs:
                        fireball.update()
                        fireball.move()
                        fireball.collision(player)
                        fireball.draw(surface)
                        if fireball.rect.right<0 or fireball.rect.left>1000 or fireball.has_hit:
                            self.fireballs.remove(fireball)
            else:
                
                if self.attack_cooldown==0:
                    self.flip=player.rect.x<self.rect.x
                    distance=abs(player.rect.x - self.rect.x)
                    if distance>150:
                        if player.rect.x<self.rect.x:
                            self.rect.x-=5
                            self.running=True
                            self.flip=True
                        elif player.rect.x>self.rect.x:
                            self.rect.x+=5
                            self.running=True
                            self.flip=False
                    else:
                        
                        attack_choice=[1,2]
                        self.attack_type=attack_choice[pygame.time.get_ticks()%2]
                        self.attack(surface,player)
                        self.attack_cooldown=20
                else:
                    self.attack_cooldown-=1
        
    def attack(self,surface,target=None):
        self.attacking=True
        self.has_hit=False
        
    def update_action(self,new_action):
        if new_action!=self.action:
            self.action=new_action
            self.frame_index=0
            self.update_time=pygame.time.get_ticks()
    def draw(self,surface):
        if self.blocking:
            self.bubble=pygame.transform.scale(self.bubble,(self.size*self.image_scale,self.size*self.image_scale))
            self.image=self.bubble
        img=pygame.transform.flip(self.image,self.flip,False)
        self.img_pos=(self.rect.x-(self.offset[0]*self.image_scale),self.rect.y-(self.offset[1]*self.image_scale))
        surface.blit(img,self.img_pos)
        self.mask=pygame.mask.from_surface(img)
class Fireball:
    def __init__(self,x,y,direction,speed,scale,sprite):
        self.speed=speed
        self.direction=direction
        self.size=180
        self.image_scale=scale
        
        self.action=0
        self.has_hit=False
        self.frame_index=0
        self.animation_list=self.load_frames(sprite,[6])
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.radiuspx=min(self.rect.width,self.rect.height)*9//2
        self.mask=pygame.mask.from_surface(self.image)
        
    def load_frames(self,sprite,animation):
        animation_list=[]
        for y,anim in enumerate(animation):
            temp_img_list=[]
            for i in range(anim):
                temp_img=sprite.subsurface(i*self.size,y*self.size,self.size,self.size)
                temp_img=pygame.transform.scale(temp_img,(self.size*self.image_scale,self.size*self.image_scale))
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list
    def collision(self,player):
        
        offset_x=player.img_pos[0] - self.rect.left
        offset_y=player.img_pos[1] - self.rect.top
        overlap=self.mask.overlap(player.mask,(offset_x,offset_y))
        if overlap and not self.has_hit:
            if not player.blocking or (player.flip and self.direction==-1) or (not player.flip and not self.direction==-1):
                 
                player.health-=30
                self.has_hit=True
            else:
                player.health-=10
                self.has_hit=True
    def update(self):
        animation_speed = 100
        now = pygame.time.get_ticks()
        if not hasattr(self, "update_time"):
            self.update_time = now
        if now - self.update_time > animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.animation_list[self.action])
            self.update_time = now
        self.image = self.animation_list[self.action][self.frame_index]
    def move(self):
        self.rect.x+=self.speed*self.direction
    def draw(self,surface):
        img=pygame.transform.flip(self.image,self.direction==-1,False)
        surface.blit(img,self.rect)
