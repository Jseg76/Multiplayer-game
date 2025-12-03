import socket as s
import pygame
import threading
import time as t
import pickle
import math as m
import random as r

win = pygame.display.set_mode((800, 600), pygame.SRCALPHA)
pygame.display.set_caption('Client')

pygame.init()

running = True
FPS = 60

canShoot = True
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
# HOST = '192.168.68.77'
HOST = '10.218.144.53'


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, c, hp, projectiles, num, dmgd):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c
        self.hp = hp
        self.projectiles = projectiles
        self.num = num
        self.dmgd = dmgd

    def move_x(self, speed):
        self.x += speed


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dmg, speed_x, speed_y, owner, collide):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.dmg = dmg
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.owner = owner
        self.collide = collide
        self.center = (self.x, self.y)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y


def take_dmg():
    player.c = color
    t.sleep(.5)
    player.c = color


def jump():
    global jumping
    jumping = True
    for i in range(7):
        player.y -= 10
        t.sleep(0.02)
    jumping = False


def shoot():
    global canShoot
    canShoot = False
    t.sleep(.3)
    canShoot = True


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


print(pygame.font.get_fonts())
font = pygame.font.Font(None, 60)
stats_font = pygame.font.SysFont('Display', 80)

stats_title_text = stats_font.render('Stats', True, (0, 0, 0))
respawn_text = font.render(f'Respawning in {respawn_time} seconds', True, (0, 0, 0, 100))

stats_menu = pygame.surface.Surface((500, 400), pygame.SRCALPHA)
stats_menu.fill((0, 0, 0, 120))

player = Player(100, 300, 30, 30, color, 100, [], r.randint(1, 100000), False)

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

            if not proj.owner == player.num and proj.x + 10 <= player.x + 30 and proj.x >= player.x and proj.y + 10 >= player.y + 10 and proj.y >= player.y:
                player.dmgd = True
                player.hp -= proj.dmg
                threading.Thread(target=take_dmg).start()

        for pro in player.projectiles:
            if not pro.owner == p.num and pro.x + 10 <= p.x + 30 and pro.x >= p.x and pro.y + 10 >= p.y + 10 and pro.y >= p.y:
                pro.collide = True
            if p.hp < 0:
                kills += 1
            if p.dmgd and not pro.owner == player.num and pro.x + 10 <= player.x + 30 and pro.x >= player.x and pro.y + 10 >= player.y + 10 and pro.y >= player.y:
                player.projectiles.pop(player.projectiles.index(pro))
            if not -300 <= pro.x <= 1100 and 900 >= pro.y >= -300:
                player.projectiles.remove(player.projectiles[player.projectiles.index(pro)])

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

    if keys[pygame.K_w] or keys[pygame.K_SPACE]:
        if 569 <= player.y <= 570:
            jumping = True
            threading.Thread(target=jump).start()

    if keys[pygame.K_TAB]:
        win.blit(stats_menu, (150, 0))
        # stats_menu.blit(stats_title_text, (150, 15))
        stats_title_text.blit(stats_menu, (150, 15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            client.close()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and canShoot:
            mouse_x, mouse_y = event.pos
            player.projectiles.append(Projectile(player.x + 15, player.y + 15, 15,
                                                 10 * m.cos(m.atan2(mouse_y - player.y + 15, mouse_x - player.x + 15)),
                                                 10 * m.sin(m.atan2(mouse_y - player.y + 15, mouse_x - player.x + 15)),
                                                 player.num, False))
            threading.Thread(target=shoot).start()

    pygame.display.flip()
    win.fill((255, 255, 255))
    clock.tick(FPS)

pygame.quit()