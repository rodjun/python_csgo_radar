import pygame

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


# TODO: Add an option to use sprites for background and player icons
class PyGameRadar(object):
    def __init__(self, size, title):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption(title)
        self.factor = 10
        self.radius = size // 2
        self.screen = pygame.display.set_mode([size, size])

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
