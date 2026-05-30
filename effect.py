import pygame, math, random

parts = []

flash = 0

def spark(x, y, color=(200, 160, 80), count=10, speed=4):
    for _ in range(count):
        angle = random.uniform(0, 6.28)
        vel = random.uniform(speed * 0.3, speed)
        lifetime = random.randint(8, 20)
        parts.append([
            float(x), float(y),
            math.cos(angle) * vel,
            math.sin(angle) * vel,
            color,
            lifetime
        ])

def explode(x, y, color=(255, 160, 40)):
    spark(x, y, color, count=18, speed=5)

def do_flash():
    global flash
    flash = 10

def update():
    global flash

    for p in parts[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[2] *= 0.9
        p[3] *= 0.9
        p[5] -= 1

        if p[5] <= 0:
            parts.remove(p)

    if flash > 0:
        flash -= 1

def draw(surface, W, H, HUD):
    for p in parts:
        radius = max(1, int(4 * p[5] / 20))
        tmp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = int(255 * p[5] / 20)
        pygame.draw.circle(tmp, (*p[4], alpha), (radius, radius), radius)
        surface.blit(tmp, (int(p[0]) - radius, int(p[1]) - radius))

    if flash > 0:
        overlay = pygame.Surface((W, H + HUD), pygame.SRCALPHA)
        overlay.fill((255, 60, 60, int(150 * flash / 10)))
        surface.blit(overlay, (0, 0))
