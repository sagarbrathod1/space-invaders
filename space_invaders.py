import pygame
from pygame import mixer
from pygame.locals import *
import random

# for the sound effects
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# define fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

# define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

# loading the sounds
explosion_fx = pygame.mixer.Sound("assets/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("assets/explosion2.wav")
explosion2_fx.set_volume(0.50)

laser_fx = pygame.mixer.Sound("assets/laser.wav")
laser_fx.set_volume(0.25)

# define game variables
rows = 5
cols = 5
last_alien_shot = pygame.time.get_ticks()
alien_cooldown = 1000     # milliseconds
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0     # 0 means game is playing, 1 means player won, -1 means player lost

# define colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# loading the background image
background = pygame.image.load("assets/space_background.png")

# function for text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_background():
    screen.blit(background, (0, 0))

# creating sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# creating the spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remain = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # setting the movement speed
        speed = 8

        # setting cooldown variable (milliseconds)
        cooldown = 500

        game_over = 0

        # obtaining key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # recording the current time
        time_current = pygame.time.get_ticks()

        # shooting bullets
        if key[pygame.K_SPACE] and time_current - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_current

        # updating masks
        self.mask = pygame.mask.from_surface(self.image)

        # drawing the health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remain > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remain / self.health_start)), 15))
        elif self.health_remain <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

# creating the bullets
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

# creating the aliens
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_dir = 1
    
    def update(self):
        self.rect.x += self.move_dir
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_dir *= -1
            self.move_counter *= self.move_dir

# generating aliens
def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens((100 + item * 100), (100 + row * 70))
            alien_group.add(alien)

# calling function to generate aliens
create_aliens()

# creating the alien bullets
class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reducing spaceship health
            spaceship.health_remain -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# creating explosions
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for n in range(1, 6):
            img = pygame.image.load(f"assets/exp{n}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1
        if self.counter >= explosion_speed and self.index < (len(self.images) - 1):
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        # if the animation is finished, delete the explosion
        if self.index >= (len(self.images) - 1) and self.counter >= explosion_speed:
            self.kill()

# creating the player
spaceship = Spaceship(int(screen_width / 2), (screen_height - 100), 3)
spaceship_group.add(spaceship)

run = True
while run:
    # frame rate
    clock.tick(fps)

    # drawing the background
    draw_background()

    if countdown == 0:
        # creating random alien bullets
        time_current = pygame.time.get_ticks()
        if (time_current - last_alien_shot) > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = AlienBullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_current
        
        # check if all aliens are eliminated
        if len(alien_group) == 0:
            game_over = 1

        if game_over == 0:
            # updating the spaceship
            game_over = spaceship.update()

            # updating the sprite groups
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else: 
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text('YOU WON!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

    if countdown > 0:
        draw_text('READY?', font40, white, int(screen_width / 2 - 75), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    # updating the explosion group
    explosion_group.update()

    # drawing the sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()