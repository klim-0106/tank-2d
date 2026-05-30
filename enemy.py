import pygame, math, random
import effect

GRN = (60, 200, 80)
RED = (220, 55, 55)
YEL = (255, 215, 50)

TILE = 48
W = TILE * 13
H = TILE * 13
HUD = 44

def draw_tank(surface, rect, color, aim_x, aim_y):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    cx, cy = rect.centerx, rect.centery

    dark = tuple(max(0, c - 80) for c in color)
    light = tuple(min(255, c + 70) for c in color)

    pygame.draw.rect(surface, dark, (x, y + 3, 6, h - 6), border_radius=2)
    pygame.draw.rect(surface, dark, (x + w - 6, y + 3, 6, h - 6), border_radius=2)

    pygame.draw.rect(surface, color, pygame.Rect(x + 6, y + 4, w - 12, h - 8), border_radius=4)
    pygame.draw.rect(surface, light, (x + 8, y + 6, w - 16, 4), border_radius=1)

    pygame.draw.rect(surface, dark, (cx - 6, cy - 6, 12, 12), border_radius=3)

    angle = math.atan2(aim_y - cy, aim_x - cx)
    barrel_end_x = int(cx + math.cos(angle) * 22)
    barrel_end_y = int(cy + math.sin(angle) * 22)
    pygame.draw.line(surface, dark, (cx, cy), (barrel_end_x, barrel_end_y), 5)

    pygame.draw.circle(surface, light, (cx, cy), 3)

class Obj:

    def __init__(self, x, y, color, speed, hp, shoot_cooldown):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = color
        self.speed = speed
        self.hp = hp
        self.cd = shoot_cooldown
        self.cd_max = shoot_cooldown
        self.dx = 0
        self.dy = 1

    def move(self, dx, dy, walls):
        if dx or dy:
            self.dx, self.dy = dx, dy

        old = self.rect.copy()

        self.rect.x += int(dx * self.speed)
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x = old.x

        self.rect.y += int(dy * self.speed)
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.y = old.y

        self.rect.x = max(0, min(W - 32, self.rect.x))
        self.rect.y = max(HUD, min(H + HUD - 32, self.rect.y))

ENEMY_CFG = [
    (1.6, 110, 1),
    (2.2, 85,  1),
    (2.8, 65,  2),
    (3.3, 50,  2),
    (3.8, 38,  3),
]

SPAWN_POINTS = [(1, 0), (5, 0), (9, 0), (0, 4), (12, 4), (1, 12), (5, 12), (9, 12)]

def spawn(level, player_rect, walls):
    speed, cooldown, hp = ENEMY_CFG[min(level - 1, 4)]

    positions = SPAWN_POINTS[:]
    random.shuffle(positions)

    enemies = []
    count = 3 + level * 2

    for i in range(count):
        col, row = positions[i % len(positions)]
        x = col * TILE + (TILE - 32) // 2
        y = HUD + row * TILE + (TILE - 32) // 2
        enemy = Obj(x, y, RED, speed, hp, cooldown)

        in_wall = any(enemy.rect.colliderect(w) for w in walls)
        if not enemy.rect.colliderect(player_rect) and not in_wall:
            enemies.append(enemy)

    return enemies

def update_enemies(enemies, player, walls, enemy_bullets):
    px, py = player.rect.center

    for e in enemies:
        cx, cy = e.rect.center
        dist = math.hypot(px - cx, py - cy)

        if dist < 260:

            vx, vy = px - cx, py - cy
            d = dist or 1
            edx = int(vx / d > 0.3) - int(vx / d < -0.3)
            edy = int(vy / d > 0.3) - int(vy / d < -0.3)
        else:

            if random.randint(0, 60) == 0:
                edx, edy = random.choice([-1, 0, 1]), 0
            else:
                edx, edy = e.dx, e.dy

        if edx and edy:
            edy = 0

        e.move(edx, edy, walls)

        e.cd -= 1
        if e.cd <= 0:
            e.cd = e.cd_max + random.randint(0, 20)
            vx, vy = px - cx, py - cy
            d = math.hypot(vx, vy) or 1
            bullet = [pygame.Rect(cx - 4, cy - 4, 8, 8), vx / d * 7, vy / d * 7]
            enemy_bullets.append(bullet)

        if e.rect.colliderect(player.rect):
            effect.do_flash()
            return True

    return False
