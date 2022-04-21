import pygame
from random import randint
from time import sleep
from threading import Thread


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.screen_width, self.screen_height = self.screen.get_size()[0], self.screen.get_size()[1]


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()[0], pygame.display.get_surface().get_size()[1]

        self.width = 96
        self.height = 96

        self.player_static = pygame.image.load('shipu1.png').convert_alpha()
        self.player_static.set_colorkey((255, 255, 255))
        self.player_static = pygame.transform.scale(self.player_static, (self.width, self.height))

        self.rect = self.player_static.get_rect()
        self.moving_right, self.moving_left, self.moving_up, self.moving_down = False, False, False, False

        self.step = 5
        self.dodge_speed = 10
        self.dodge_length = 200
        self.dodging = False
        self.dodge_active = True
        self.dodge_cooldown = 5
        self.current_dodge_cooldown = 0

        self.game = game

        self.s_lives = 1
        self.lives = self.s_lives

        self.screenW_range = range(0, self.screen_width)
        self.screenH_range = range(0, self.screen_height)

        self.thread1 = Thread(target=self.dodge_cd)
        self.thread1.start()

    def move(self, dt, target_fps):
        dt = dt * target_fps
        if self.moving_up:
            self.move_up(dt)

        if self.moving_down:
            self.move_down(dt)

        if self.moving_left:
            self.move_left(dt)

        if self.moving_right:
            self.move_right(dt)

    def move_up(self, dt):
        if self.rect.top >= pygame.display.get_surface().get_rect().top:
            self.rect.y -= int(self.step * dt)

    def move_down(self, dt):
        if self.rect.bottom <= pygame.display.get_surface().get_rect().bottom:
            self.rect.y += int(self.step * dt)

    def move_left(self, dt):
        if self.rect.left >= pygame.display.get_surface().get_rect().left:
            self.rect.x -= int(self.step * dt)

    def move_right(self, dt):
        if self.rect.right <= pygame.display.get_surface().get_rect().right:
            self.rect.x += int(self.step * dt)

    def dodge_cd(self):
        while True:
            if not self.game.running:
                break
            if not self.dodge_active:
                for i in range(0, 5):
                    if self.dodge_active:
                        break
                    self.current_dodge_cooldown = (5 - i)
                    sleep(1)

                self.current_dodge_cooldown = 0
                self.dodge_active = True
                print("EXECUTED", self.dodge_active)
            else:
                sleep(0.1)

    def dodge(self, last_keys_main, dt, target_fps):
        dt = dt * target_fps
        right = round(self.rect.right + self.dodge_length)
        left = round(self.rect.left - self.dodge_length)
        top = round(self.rect.top - self.dodge_length)
        bottom = round(self.rect.bottom + self.dodge_length)
        len_last_keys = len(last_keys_main)
        last_keys = [last_keys_main[-1]] if len_last_keys == 1 else [last_keys_main[-2], last_keys_main[-1]]

        if last_keys[0] == "w" and last_keys[-1] == "d" or last_keys[0] == "d" and last_keys[-1] == "w":
            if right in self.screenW_range and top in self.screenH_range:
                self.dodge_right()
                self.dodge_up()
                self.dodge_active = False

        elif last_keys[0] == "w" and last_keys[-1] == "a" or last_keys[0] == "a" and last_keys[-1] == "w":
            if left in self.screenW_range and top in self.screenH_range:
                self.dodge_left()
                self.dodge_up()
                self.dodge_active = False

        elif last_keys[0] == "s" and last_keys[-1] == "a" or last_keys[0] == "a" and last_keys[-1] == "s":
            if left in self.screenW_range and bottom in self.screenH_range:
                self.dodge_left()
                self.dodge_down()
                self.dodge_active = False

        elif last_keys[0] == "s" and last_keys[-1] == "d" or last_keys[0] == "d" and last_keys[-1] == "s":
            if right in self.screenW_range and bottom in self.screenH_range:
                self.dodge_right()
                self.dodge_down()
                self.dodge_active = False

        elif last_keys[-1] == "d" and right in self.screenW_range:
            self.dodge_right()
            self.dodge_active = False

        elif last_keys[-1] == "w" and top in self.screenH_range:
            self.dodge_up()
            self.dodge_active = False

        elif last_keys[-1] == "a" and left in self.screenW_range:
            self.dodge_left()
            self.dodge_active = False

        elif last_keys[-1] == "s" and bottom in self.screenH_range:
            self.dodge_down()
            self.thread1.start()
            self.dodge_active = False

        self.dodging = False

    def dodge_right(self):
        self.rect.x += round(self.dodge_length)

    def dodge_left(self):
        self.rect.x -= round(self.dodge_length)

    def dodge_up(self):
        self.rect.y -= round(self.dodge_length)

    def dodge_down(self):
        self.rect.y += round(self.dodge_length)

    def start_pos(self):
        self.rect.x = self.screen_width / 2 - self.width / 2
        self.rect.y = self.screen_width - self.height

    def restart(self):
        self.start_pos()
        self.lives = self.s_lives
        self.current_dodge_cooldown = 0
        self.dodging = False
        self.dodge_active = True

    def update(self):
        pygame.display.get_surface().blit(self.player_static, (self.rect.x, self.rect.y))


class Bullet(Entity):
    def __init__(self, pos_x, pos_y):
        super().__init__()

        self.width = 6
        self.height = 20

        self.speed = 10

        self.image = pygame.image.load('bullet.bmp').convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update(self, dt, target_fps):
        dt = dt * target_fps
        self.rect.y -= self.speed * dt
        if self.rect.bottom < self.screen_rect.top:
            self.kill()
            print("ded too")


class Alien(Entity):
    def __init__(self, image, size, x, y, direction, lives, stop_x=None, stop_y=None):
        super().__init__()
        self.size = size

        self.x = float(x)
        self.y = float(y)
        self.direction = direction

        self.stop_x = None if type(stop_x) is not range else stop_x
        self.stop_y = None if type(stop_y) is not range else stop_y
        print(True if 0 in self.stop_x else False)

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect(midbottom=(float(self.x), float(self.y)))

        self.lives = lives


class Meteor(Entity):
    def __init__(self, image, size, x, y):
        super().__init__()
        rand_size = randint(size - 15, size + 15)
        # print(rand_size)
        self.width = rand_size
        self.height = rand_size

        self.x = x
        self.y = y

        self.vely = 0
        self.maxvel = randint(6, 17)
        accel = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5]
        self.accel = accel[randint(0, 5)]

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey((255, 255, 255))

        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self, dt, target_fps):
        dt = dt * target_fps
        if self.rect.top <= self.screen_rect.bottom:
            if not self.vely > self.maxvel:
                self.vely += self.accel

        else:
            # print("ded")
            self.kill()
        # print(self.vely)
        self.rect.y += self.vely * dt

        self.screen.blit(self.image, (self.rect.x, self.rect.y))
