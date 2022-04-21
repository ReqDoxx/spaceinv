import pygame
import time
from sys import exit
from vfx import Background
from entities import Player
from gui import Menu, Game_Graphics
from threading import Timer
from game_events import Events
from threading import Thread


class Game:
    def __init__(self):
        pygame.init()
        # screen
        self.screen_width, self.screen_height = 800, 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.DOUBLEBUF,
                                              pygame.OPENGLBLIT)
        self.screen_rect = self.screen.get_rect()

        pygame.display.set_caption("Space invaders")

        self.dt = 0
        self.FPS = 60
        self.TARGET_FPS = 60
        self.FPS_possible = [30, 60]

        self.direction = "UP"

        self.now = 0
        self.prev_time = time.time()

        self.pressed_wasd_list = list()

        self.clock = pygame.time.Clock()
        self.gui_font = pygame.font.Font("ArcadeClassic.ttf", 30)

        # objects
        self.playing = False
        self.running = True
        self.display_menu = True
        self.lost = False

        self.pressed_once = False
        self.can_held = False
        self.held = False

        self.background = Background(self)
        self.player = Player(self)
        self.menu = Menu(self)
        self.game_gui = Game_Graphics()
        self.event_manager = Events()

        pygame.mixer.music.load('click1.wav')
        self.click_sound = pygame.mixer.Sound('click1.wav')
        self.click_sound.set_volume(self.menu.current_volume)

    def on_start(self):
        self.player.start_pos()

    def loops(self):
        #  game loop
        while True:
            print(1)
            self.menu_loop()
            if not self.running:
                print("LOL")
                break
            print(2)
            self.on_game_start()
            self.game_loop()
            if not self.running:
                break

    def on_game_start(self):
        # thread = Thread(target=self.dodge_check, args=(1,))
        # thread.start()
        self.event_manager.spawn_aliens()

    def game_loop(self):
        self.playing = True
        while self.playing:
            if not self.running:
                break

            self.FPS_independence()

            self.check_key_events()
            self.player.move(self.dt, self.TARGET_FPS)

            self.event_manager.spawn_meteors()

            self.event_manager.collisions_check(self.player, self)
            self.event_manager.move_aliens(self.dt, self.TARGET_FPS)
            self.background.move(self.dt)
            self.update_game_screen()

    # def dodge_check(self, seconds):
    #     while True:
    #         time.sleep(seconds)
    #         print(f"Dodging {self.player.dodging}\nDodge active {self.player.dodge_active}\n")

    def menu_loop(self):
        self.display_menu = True
        while self.display_menu:
            if not self.running:
                break
            self.FPS_independence()
            self.check_key_events()
            self.background.move(self.dt)
            self.update_menu_screen()

    def check_key_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.check_key_down_events(event)

            if event.type == pygame.KEYUP:
                self.check_key_up_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.pressed_once = True
                self.menu.buttons_clicked()
                t = Timer(2, self.allow_held)
                t.start()

            # <here> Left mouse button up events </here>
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.pressed_once = False
                self.disable_held()
                try:
                    t.cancel()
                except:
                    pass

        if self.pressed_once and self.can_held:
            self.menu.buttons_held()

    def check_key_down_events(self, event):
        if event.key == pygame.K_d:
            self.player.moving_right = True
            self.pressed_wasd_list.append("d")

        elif event.key == pygame.K_a:
            self.player.moving_left = True
            self.pressed_wasd_list.append("a")

        elif event.key == pygame.K_w:
            self.player.moving_up = True
            self.pressed_wasd_list.append("w")

        elif event.key == pygame.K_s:
            self.player.moving_down = True
            self.pressed_wasd_list.append("s")

        elif event.key == pygame.K_SPACE:
            if len(self.event_manager.bullet_group) <= 5:
                self.event_manager.create_bullet(self.player.rect)

        elif event.key == pygame.K_LSHIFT and self.pressed_wasd_list and self.player.dodge_active and self.playing:
            self.player.dodge(self.pressed_wasd_list, self.dt, self.TARGET_FPS)

    def check_key_up_events(self, event):
        if event.key == pygame.K_d:
            self.player.moving_right = False
            self.pressed_wasd_list.remove("d")

        elif event.key == pygame.K_a:
            self.player.moving_left = False
            self.pressed_wasd_list.remove("a")

        elif event.key == pygame.K_w:
            self.player.moving_up = False
            self.pressed_wasd_list.remove("w")

        elif event.key == pygame.K_s:
            self.player.moving_down = False
            self.pressed_wasd_list.remove("s")

    def allow_held(self):
        self.can_held = True

    def disable_held(self):
        self.can_held = False

    def FPS_independence(self):
        self.clock.tick(self.FPS)
        self.now = time.time()
        self.dt = self.now - self.prev_time
        self.prev_time = self.now

    def update_game_screen(self):
        self.background.update()

        self.event_manager.bullet_group.draw(self.screen)
        self.event_manager.bullet_group.update(self.dt, self.TARGET_FPS)

        self.event_manager.update(self.dt, self.TARGET_FPS)

        self.player.update()
        self.game_gui.draw_dodge_cd(self.player)
        pygame.display.flip()

    def lose(self):
        self.playing = False
        self.lost = True

    def update_menu_screen(self):
        self.background.update()
        self.menu.main_menu_update()
        pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.on_start()
    game.loops()
    pygame.quit()
