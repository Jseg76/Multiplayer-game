import socket as s
import pygame
import threading
import time as t
import pickle
import math as m
import random as r
import pygame.freetype

win = pygame.display.set_mode((800, 600))
alpha_win = pygame.Surface((800, 600), pygame.SRCALPHA)

pygame.display.set_caption('Client')

pygame.init()

running = True
FPS = 60

possible_jump = False
jumping = False
respawn_time = 0
respawning = False
max_speed = 30

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
# HOST = '192.168.68.71'
HOST = '10.218.144.53'

username_input = True
input = False
input_text = ''

total_messages = [[],[],[],[],[],[],[],[],[],[]]
all_messages = ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',]
message_number = 0
msg_len = -1

class Map:
    def __init__(self, bg, blocks):
        self.bg = bg
        self.blocks = blocks

class Block:
    def __init__(self, color, x, y, width, height):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.top = range(self.x, self.x + self.width)
        self.left = range(self.y, self.y + self.height)

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
        self.user = ''
        self.messages = []
        self.msg_index = 0

    def move_x(self, speed):
        self.x += speed

    def gravity(self, gravity):
        self.y += gravity

    def take_dmg(self):
        self.c = color
        t.sleep(.5)
        self.c = color

    def shoot(self):
        self.canShoot = False
        t.sleep(.3)
        self.canShoot = True

    def jump(self, speed, time):
        self.jumping = True
        for i in range(time):
            player.y -= speed
            if speed < max_speed:
                speed += speed
            t.sleep(1)
        # t.sleep(1)
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

def text_input(text, maxLen, size, color, dest):
    global inputText_w, inputText_h, user_max_len
    inputFont = pygame.font.Font(None, size)
    inputText = inputFont.render(text, True, color)
    inputText.set_alpha(200)
    win.blit(inputText, dest)
    inputText_w = inputText.get_width()
    inputText_h = inputText.get_height()
    user_max_len = maxLen


def draw_text(text, size, color, dest, alpha):
    global text_w, text_h
    font = pygame.font.Font(None, size)
    text = font.render(text, True, color)
    text.set_alpha(alpha)
    win.blit(text, dest)
    text_w = text.get_width()
    text_h = text.get_height()

def text_bg(w, h, color, dest):
    text_Bg = pygame.surface.Surface((w, h), pygame.SRCALPHA)
    text_Bg.fill(color)
    win.blit(text_Bg, dest)

def username(user, size, color, dest):
    global username_w
    userFont = pygame.font.Font(None, size)
    usernameText = userFont.render(user, True, color)
    win.blit(usernameText, dest)
    username_w = usernameText.get_width()

def save_data(data):
    with open('data.txt', 'wb') as file:
        pickle.dump(data, file)

maps = [[(219, 208, 82), Block((156, 118, 43), 0, 560, 800, 40)]]

map = Map((255, 255, 255), [])

map_number = r.randint(0, len(maps) - 1)
chosen_map = maps[map_number]
map.bg = chosen_map[0]

for block in chosen_map:
    if block != chosen_map[0]:
        map.blocks.append(block)

print(map.blocks)

username('', 30, (255, 255, 255), (0, 0))

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
        if username_input:
            with open('data.txt', 'rb') as file:
                data = pickle.load(file)
                if len(data) > 0:
                    player.user = data
                    username_input = False
                else:
                    username_input = True
    except:
        pass
    try:
        client.send(pickle.dumps(player))
        players = pickle.loads(client.recv(4096))
    except:
        pass

    win.blit(alpha_win, (0, 0))

    for block in map.blocks:
        pygame.draw.rect(win, block.color, block.rect)
        if not jumping and not player.rect.collidepoint(block.x, block.y):
            player.gravity(9.8)

    for projectile in player.projectiles:
        projectile.move()

    player.rect = pygame.Rect(player.x, player.y, player.w, player.h)
    pygame.draw.rect(stats_menu, (255, 0, 0, 120), (100, 100, 50, 50))

    for p in players:
        if message_number < len(players)-1:
            message_number += 1
        else:
            message_number = 0
        if p.hp > 0:
            try:
                if not username_input:
                    username(p.user, 30, BLACK, (p.x + 15 - username_w/2, p.y - 40))
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
            if pro.rect.colliderect(p.rect) and pro.owner != p.id and p.dmgd:
                player.projectiles.pop(player.projectiles.index(pro))
                if p.hp < 0:
                    kills += 1

            if not -300 <= pro.x <= 1100 and 900 >= pro.y >= -300:
                player.projectiles.pop(player.projectiles.index(pro))

        for message in p.messages:
            total_messages[message_number] = p.messages
            for msgs in total_messages:
                if not len(msgs) == 0:
                    for msg in msgs:
                        if msg.replace(' ', '') != '':
                            all_messages[sum(len(msgs) for msgs in total_messages)] = msg
                            print(all_messages)

    for Msg in all_messages:
        if Msg.replace(' ', '') != '':
            draw_text(Msg, 50, (0, 0, 0), (3, 570 - all_messages.index(Msg)*35), 200)
            text_bg(max(text_w + 5, 200), 35, (0, 0, 0, 120), (3, 570 - all_messages.index(Msg)*35))

    if player.x > 770:
        player.x = 770
    if player.x < 0:
        player.x = 0
    if player.y > 560:
        player.y = 560
    if player.y < 0:
        player.y = 0

    keys = pygame.key.get_pressed()
    if player.hp > 0:
        respawning = False
        if not input and not username_input:
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

    if not input and not username_input:
        if keys[pygame.K_w] or keys[pygame.K_SPACE] and player.hp > 0:
            # if 569 <= player.y <= 570:
            #     player.jumping = True
            if not player.jumping:
                threading.Thread(target=player.jump(30, 1)).start()

    if keys[pygame.K_TAB] and not username_input:
        win.blit(stats_menu, (150, 0))
        # stats_menu.blit(stats_title_text, (180, 30))

    if username_input:
        text_input(player.user, 10, 80, BLACK, (300, 300))
        text_bg(max(inputText_w, 200), inputText_h, (120, 120, 120, 120), (300, 300))

    if input:
        text_input(input_text, 50, 50, (0, 0, 0, 120), (0, 565))
        text_bg(max(inputText_w+5, 200), inputText_h+10, (0, 0, 0, 120), (0, 565))

    if username_input:
        if keys[pygame.K_e]:
            pass
    for event in pygame.event.get():
        if username_input and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                player.user = player.user[:-1]
            elif event.key == pygame.K_RETURN:
                username_input = False
                save_data(player.user)
            elif event.key == pygame.K_ESCAPE:
                username_input = False
            elif event.key == pygame.K_TAB:
                pass
            elif len(player.user) + 1 <= user_max_len:
                player.user += event.unicode


        # if keys[pygame.K_c] and not username_input:
        #     input = True
        # if not username_input and input and event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_ESCAPE:
        #         input = False
        #     elif event.key == pygame.K_BACKSPACE:
        #         input_text = input_text[:-1]
        #     elif event.key == pygame.K_RETURN:
        #         input = False
        #         if not input_text.replace(' ','') == '' and not f'<{player.user}> {input_text}' in player.messages:
        #             player.messages.append(f'<{player.user}> {input_text}')
        #             player.msg_index += 1
        #         input_text = ""
        #     elif len(input_text) <= 26:
        #         input_text += event.unicode


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.canShoot and player.hp > 0 and not input and not username_input:
            mouse_x, mouse_y = event.pos
            player.projectiles.append(Projectile(player.x + 15, player.y + 15, 15, 10 * m.cos(
                m.atan2(mouse_y - 20 - player.y + 15, mouse_x - 20 - player.x + 15)), 10 * m.sin(
                m.atan2(mouse_y - 20 - player.y + 15, mouse_x - 20 - player.x + 15)), player.id))
            threading.Thread(target=player.shoot).start()

        if event.type == pygame.QUIT:
            client.close()
            running = False

    pygame.display.flip()
    win.fill((map.bg))
    clock.tick(FPS)

pygame.quit()