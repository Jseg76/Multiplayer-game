import socket as s
import threading
import pygame
import pickle


PORT = 8000
HOST = s.gethostbyname(s.gethostname())


players = -1
player_data = []


server = s.socket(s.AF_INET, s.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(10)
print("server is listening on " + HOST)


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
            self.y -= 9
            t.sleep(0.02)
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


def handle_client(conn, addr):
    global players
    players += 1
    clientNum = players
    print(clientNum)


    while True:
        try:
            data = pickle.loads(conn.recv(4096))


        except:
            conn.close()
            while True:
                try:
                    player_data.pop(clientNum)
                    break
                except:
                    clientNum -= 1


            players -= 1
            print('connection closed')
            break
        try:
            player_data[clientNum] = data
            conn.send(pickle.dumps(player_data))
        except:
            pass
while True:
    conn, addr = server.accept()
    player_data.append(players)


    threading.Thread(target=handle_client, args=(conn, addr)).start()




