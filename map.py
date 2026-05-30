import pygame, math

TILE = 48
W = TILE * 13
H = TILE * 13
HUD = 44

BRK = (180, 75, 25)
STL = (120, 130, 150)
GLD = (255, 200, 0)

CHICKEN_IMG = None

MAP = [
    "..B..B..B..",
    "BBB.BBB.BBB",
    "B.B.B.B.B.B",
    "BBB.BBB.BBB",
    "...........",
    "BB.SSS.SSS.",
    "B..S.S.S.SB",
    "BB.SSS.SSS.",
    "...........",
    "BBB.BBB.BBB",
    "B.B.B.B.B.B",
    "BBB.BBB.BBB",
    ".....F.....",
]

def build():
    """Создаёт словарь тайлов и возвращает прямоугольник флага."""
    tiles = {}
    flag_rect = None

    for row, line in enumerate(MAP):
        for col, ch in enumerate(line):
            if ch in ('B', 'S', 'F'):
                rect = pygame.Rect(col * TILE, HUD + row * TILE, TILE, TILE)
                hp = 2 if ch == 'B' else 9
                tiles[(col, row)] = [ch, hp, rect]
                if ch == 'F':
                    flag_rect = rect

    return tiles, flag_rect

def walls_from(tiles):
    """Возвращает список прямоугольников всех непроходимых стен."""
    return [data[2] for data in tiles.values() if data[0] in ('B', 'S')]

def draw_tiles(surface, tiles):
    """Рисует все тайлы на экране."""
    global CHICKEN_IMG

    if CHICKEN_IMG is None:
        try:
            CHICKEN_IMG = pygame.image.load('chicken.png').convert_alpha()
            CHICKEN_IMG = pygame.transform.scale(CHICKEN_IMG, (TILE, TILE))
        except Exception:

            CHICKEN_IMG = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.circle(CHICKEN_IMG, GLD, (TILE // 2, TILE // 2), TILE // 3)

    for kind, hp, r in tiles.values():

        if kind == 'B':

            pygame.draw.rect(surface, BRK, r)

            for row in range(2):
                for col in range(2):
                    brick = pygame.Rect(
                        r.x + col * r.w // 2 + 1,
                        r.y + row * r.h // 2 + 1,
                        r.w // 2 - 2,
                        r.h // 2 - 2
                    )
                    pygame.draw.rect(surface, BRK, brick)
                    pygame.draw.line(surface, (220, 110, 60), (brick.x, brick.y), (brick.right, brick.y), 1)
                    pygame.draw.line(surface, (80, 30, 5), (brick.x, brick.bottom), (brick.right, brick.bottom), 1)
            pygame.draw.rect(surface, (60, 25, 5), r, 1)

            if hp <= 1:
                pygame.draw.line(surface, (50, 20, 5), (r.x + 4, r.y + 4), (r.centerx, r.centery), 2)
                pygame.draw.line(surface, (50, 20, 5), (r.centerx, r.centery), (r.right - 4, r.bottom - 4), 2)

        elif kind == 'S':

            pygame.draw.rect(surface, STL, r)
            pygame.draw.rect(surface, (180, 195, 220), pygame.Rect(r.x, r.y, r.w, 3))
            pygame.draw.rect(surface, (40, 45, 60), r, 2)

        elif kind == 'F':

            t = pygame.time.get_ticks() / 500
            glow = int(22 + 8 * math.sin(t))
            cx, cy = r.centerx, r.centery

            glow_surf = pygame.Surface((glow * 2, glow * 2), pygame.SRCALPHA)
            alpha = int(100 + 60 * math.sin(t))
            pygame.draw.circle(glow_surf, (*GLD, alpha), (glow, glow), glow)
            surface.blit(glow_surf, (cx - glow, cy - glow))

            surface.blit(CHICKEN_IMG, r.topleft)

def make_bg():
    """Создаёт фон из клеток в шахматном порядке."""
    bg = pygame.Surface((W, H))
    c1 = (18, 20, 28)
    c2 = (22, 25, 35)

    for gy in range(0, H, TILE):
        for gx in range(0, W, TILE):
            color = c1 if (gx // TILE + gy // TILE) % 2 == 0 else c2
            pygame.draw.rect(bg, color, (gx, gy, TILE, TILE))

    return bg
