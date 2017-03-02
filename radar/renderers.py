import pygame
import subprocess
import time
import struct
import socket
import os

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


class RemoteRadar(object):
    def __init__(self, config):
        print("Loading remote radar")
        print("Launching server...")
        current_path = os.getcwd()
        server_path = os.path.join(current_path, "radar")
        print(server_path)
        #subprocess.Popen(['python', 'server.py'], cwd=server_path)
        print("Done, sleeping for 3sec to make sure that the server is running...")
        time.sleep(3)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((config['ip'], config['port']))
        print("If nothing went wrong, we should be here. I know that because there's no error handling")

    def update(self, x, y, color, visible):
        enemies = []
        friends = []
        for row in zip(x, y, color):
            if row[2] == 0:
                friends += (row[0], row[1])
            else:
                enemies += (row[0], row[1])

        enemies.extend([-1] * (32 - len(enemies)))
        friends.extend([-1] * (32 - len(friends)))

        final = [0]
        final.extend(enemies)
        final.extend(friends)
        if len(final) != 65:
            print("len != 55, len =", len(final))
        self.s.send(struct.pack("h" * 65, *map(int, final)))




# TODO: Add an option to use sprites for background and player icons
class PyGameRadar(object):
    def __init__(self, config):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption(config['window_title'])
        self.factor = 10
        self.radius = config['size'] // 2
        self.screen = pygame.display.set_mode([config['size'], config['size']])

    def draw_background(self):
        self.screen.fill(Color.BLACK)
        pygame.draw.circle(self.screen, Color.BLUE, [self.radius, self.radius], self.radius)
        pygame.draw.line(self.screen, Color.WHITE, (0, self.radius), (self.radius * 2, self.radius))
        pygame.draw.line(self.screen, Color.WHITE, (self.radius, 0), (self.radius, self.radius * 2))

    def draw_player(self, x, y, enemy, visible):
        color = Color.RED if enemy else Color.GREEN
        pygame.draw.circle(self.screen, color, (int(y), int(x)), 6 if visible else 3)

    def update(self, x, y, color, visible):
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit()

        self.draw_background()

        for x, y, color, visible in zip(x, y, color, visible):
            self.draw_player(x, y, color, visible)
        pygame.display.update()
