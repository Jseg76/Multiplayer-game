import socket as s

import pygame
import threading
import time as t
import pickle
import math as m
import random as r
import pygame.freetype

win = pygame.display.set_mode((800, 600), pygame.SRCALPHA)
pygame.display.set_caption('Client')

pygame.init()

running = True
FPS = 60

possible_jump = False
jumping = False
respawn_time = 0
respawning = False

kills = 0
deaths = 0

players = []

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

color = RED

clock = pygame.time.Clock()
PORT = 8000
# HOST = '192.168.68.76'


HOST = '10.218.144.53'


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, c, hp, id):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c
        self.hp = hp
        self.projectiles = []
        self.id = id
        self.rect = pygame.Rect(x, y, w, h)
        self.canShoot = True
        self.jumping = False
        self.dmgd = False
        self.immune = False

    def move_x(self, speed):
        self.x += speed
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def take_dmg(self):
        self.c = color
        t.sleep(.5)
        self.c = color

    def shoot(self):
        self.canShoot = False
        t.sleep(.3)
        self.canShoot = True

    def jump(self):
        self.jumping = True
        for i in range(8):
            self.y -= 16
            t.sleep(0.01)
        self.jumping = False

    def immunity(self):
        self.immune = True
        t.sleep(.4)
        self.immune = False

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dmg, speed_x, speed_y, owner):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.dmg = dmg
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.owner = owner
        self.center = (self.x, self.y)
        self.rect = pygame.Rect(x, y, 10, 10)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect = pygame.Rect(self.x, self.y, 10, 10)


def respawn():
    global respawn_time, respawn_text, canShoot
    respawn_time = 5
    for i in range(respawn_time):
        respawn_text = font.render(f'Respawning in {respawn_time} seconds', True, BLACK)
        t.sleep(1)
        respawn_time -= 1
        canShoot = True

    player.hp = 100
    player.x, player.y = 400, 500


font = pygame.font.Font(None, 60)
stats_font = pygame.freetype.SysFont(None, 80)

stats_title_text = stats_font.render('Stats', (0, 0, 0, 100))
respawn_text = font.render(f'Respawning in {respawn_time} seconds', True, BLACK)

stats_menu = pygame.surface.Surface((500, 400), pygame.SRCALPHA)
stats_menu.fill((0, 0, 0, 120))

player = Player(100, 300, 30, 30, color, 100, r.randint(1, 100000))

client = s.socket(s.AF_INET, s.SOCK_STREAM)

while True:
    try:
        client.connect((HOST, PORT))
        break
    except:
        print("failed to connect")

while running:
    try:
        client.send(pickle.dumps(player))
        players = pickle.loads(client.recv(4096))
    except:
        pass

    for projectile in player.projectiles:
        projectile.move()

    for p in players:
        if p.hp > 0:
            try:
                pygame.draw.rect(win, p.c, (p.x, p.y, p.w, p.h))
                pygame.draw.rect(win, (0, 0, 0), (p.x - 10, p.y - 20, 50, 10))
                pygame.draw.rect(win, (200, 0, 0), (p.x - 7, p.y - 17, 44 * p.hp / 100, 4))
            except:
                pass

        for proj in p.projectiles:

            if 0 <= proj.x <= 800 and 600 >= proj.y >= 0:
                pygame.draw.circle(win, (0, 0, 0), (proj.x, proj.y), 5)

            if proj.owner != player.id and proj.rect.colliderect(player.rect) and not player.immune:
                threading.Thread(target=player.immunity).start()
                player.dmgd = True
                player.hp -= proj.dmg
                threading.Thread(target=player.take_dmg).start()
            else:
                player.dmgd = False

        for pro in player.projectiles:
            if pro.rect.colliderect(p.rect) and pro.owner != p.id:
                if p.dmgd:
                    player.projectiles.pop(player.projectiles.index(pro))
                    if p.hp < 0:
                        kills += 1

            if not -300 <= pro.x <= 1100 and 900 >= pro.y >= -300:
                player.projectiles.pop(player.projectiles.index(pro))

    if player.x > 770:
        player.x = 770
    if player.x < 0:
        player.x = 0
    if player.y > 560:
        player.y = 560
    if player.y < 0:
        player.y = 0

    if not jumping:
        player.y += 9.8

    keys = pygame.key.get_pressed()
    if player.hp > 0:
        respawning = False
        if keys[pygame.K_a]:
            player.move_x(-3)
        if keys[pygame.K_d]:
            player.move_x(3)
    else:
        deaths += 1
        player.x, player.y = -40, 500
        canShoot = False
        if not respawning:
            threading.Thread(target=respawn).start()
            respawning = True
        win.blit(respawn_text, (150, 100))

    if keys[pygame.K_w] or keys[pygame.K_SPACE] and player.hp > 0:
        if 569 <= player.y <= 570:
            player.jumping = True
            threading.Thread(target=player.jump).start()

    if keys[pygame.K_TAB]:
        win.blit(stats_menu, (150, 0))
        # stats_menu.blit(stats_title_text, (180, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            client.close()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.canShoot and player.hp > 0:
            mouse_x, mouse_y = event.pos
            player.projectiles.append(Projectile(player.x + 15, player.y + 15, 15, 10 * m.cos(m.atan2(mouse_y -20 - player.y + 15, mouse_x -20 - player.x + 15)), 10 * m.sin(m.atan2(mouse_y -20 - player.y + 15, mouse_x -20 - player.x + 15)), player.id))
            threading.Thread(target=player.shoot).start()

    pygame.display.flip()
    win.fill((255, 255, 255))
    clock.tick(FPS)

pygame.quit()


