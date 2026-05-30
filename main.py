import pygame, sys, math, random
import effect
import map as mp
import enemy as en

pygame.init()
pygame.mixer.init()

W, H, HUD = mp.W, mp.H, mp.HUD
screen = pygame.display.set_mode((W, H + HUD))
pygame.display.set_caption("Захват Флага")
clock = pygame.time.Clock()

pygame.mixer.music.load('rammstein-du-hast.mp3')
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)

shoot_sfx = pygame.mixer.Sound('SHOOT011.mp3')
shoot_sfx.set_volume(0.6)

FONT = pygame.font.SysFont("Consolas", 22, bold=True)

BLK = (10, 12, 18)
WHT = (255, 255, 255)
GRN = (60, 200, 80)
YEL = (255, 215, 50)
RED = (220, 55, 55)
GLD = (255, 200, 0)

def run_level(lvl):                                                           

    tiles, flag_rect = mp.build()
    walls = mp.walls_from(tiles)
    bg = mp.make_bg()

    player = en.Obj(W // 2 - 16, HUD + 16, en.GRN, speed=3, hp=1, shoot_cooldown=0)
    enemies = en.spawn(lvl, player.rect, walls)

    player_bullets = []
    enemy_bullets = []
    shoot_cooldown = 0

    effect.parts.clear()
    effect.flash = 0

    screen_bounds = pygame.Rect(0, 0, W, H + HUD)

    def move_bullet(bullet):                                                   
        bullet[0].x += int(bullet[1])
        bullet[0].y += int(bullet[2])

        for key, (kind, hp, r) in list(tiles.items()):
            if kind == 'S':
                continue
            if kind == 'B' and bullet[0].colliderect(r):
                tiles[key][1] -= 1
                effect.spark(bullet[0].centerx, bullet[0].centery)
                if tiles[key][1] <= 0:
                    del tiles[key]
                    walls[:] = mp.walls_from(tiles)
                return False

        return screen_bounds.contains(bullet[0])

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and shoot_cooldown == 0:
                cx, cy = player.rect.center
                vx, vy = mx - cx, my - cy
                d = math.hypot(vx, vy) or 1
                player_bullets.append([pygame.Rect(cx - 4, cy - 4, 8, 8), vx / d * 10, vy / d * 10])
                shoot_sfx.play()
                shoot_cooldown = 16

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        if dx and dy:
            dy = 0

        player.move(dx, dy, walls)

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if pygame.mouse.get_pressed()[0] and shoot_cooldown == 0:
            cx, cy = player.rect.center
            vx, vy = mx - cx, my - cy
            d = math.hypot(vx, vy) or 1
            player_bullets.append([pygame.Rect(cx - 4, cy - 4, 8, 8), vx / d * 10, vy / d * 10])
            shoot_sfx.play()
            shoot_cooldown = 16

        if flag_rect and player.rect.colliderect(flag_rect):
            return True

        for b in player_bullets[:]:
            if not move_bullet(b):
                player_bullets.remove(b)
                continue
            for e in enemies[:]:
                if b[0].colliderect(e.rect):
                    effect.explode(e.rect.centerx, e.rect.centery)
                    e.hp -= 1
                    if e.hp <= 0:
                        enemies.remove(e)
                    if b in player_bullets:
                        player_bullets.remove(b)
                    break

        player_dead = False
        for b in enemy_bullets[:]:
            if not move_bullet(b):
                enemy_bullets.remove(b)
                continue
            if b[0].colliderect(player.rect):
                effect.explode(player.rect.centerx, player.rect.centery, (80, 160, 255))
                effect.do_flash()
                enemy_bullets.remove(b)
                player_dead = True
                break

        if not player_dead:
            player_dead = en.update_enemies(enemies, player, walls, enemy_bullets)

        effect.update()

        screen.fill(BLK)
        screen.blit(bg, (0, HUD))
        mp.draw_tiles(screen, tiles)

        for b in enemy_bullets:
            pygame.draw.rect(screen, RED, b[0], border_radius=3)
        for b in player_bullets:
            pygame.draw.rect(screen, YEL, b[0], border_radius=3)

        px, py = player.rect.center
        for e in enemies:
            en.draw_tank(screen, e.rect, en.RED, px, py)
        en.draw_tank(screen, player.rect, en.GRN, mx, my)

        effect.draw(screen, W, H, HUD)

        pygame.draw.rect(screen, (15, 18, 30), (0, 0, W, HUD))
        pygame.draw.line(screen, (45, 55, 85), (0, HUD), (W, HUD), 2)
        screen.blit(FONT.render(f"LVL {lvl}/5", True, YEL), (8, 9))
        screen.blit(FONT.render(f"Охрана: {len(enemies)}", True, RED), (W - 140, 9))
        hint = FONT.render("WASD + ЛКМ — дойди до курицы!", True, (55, 70, 100))
        screen.blit(hint, hint.get_rect(center=(W // 2, HUD // 2)))

        pygame.display.flip()

        if player_dead:
            pygame.time.delay(500)
            return False

def wait_for_key():
    """Ждёт нажатия любой клавиши."""
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                return

def show_message(title, subtitle, title_color=YEL):
    """Показывает экран с сообщением и ждёт клавиши."""
    overlay = pygame.Surface((W, H + HUD), pygame.SRCALPHA)
    overlay.fill((8, 10, 20, 220))
    screen.blit(overlay, (0, 0))

    for text, y, color in [
        (title,               H // 2 - 40, title_color),
        (subtitle,            H // 2 + 10, WHT),
        ("ENTER — продолжить", H // 2 + 55, GRN),
    ]:
        rendered = FONT.render(text, True, color)
        screen.blit(rendered, rendered.get_rect(center=(W // 2, y)))

    pygame.display.flip()
    wait_for_key()

LEVEL_DESCS = [
    "Дойди до курицы!",
    "Охрана быстрее.",
    "Бронированные враги.",
    "Элита на месте.",
    "ФИНАЛ. Удачи!",
]

show_message("ЗАХВАТ КУРИЦЫ", "Пробейся сквозь охрану к курице!")

while True:
    for lvl in range(1, 6):
        show_message(f"УРОВЕНЬ {lvl}", LEVEL_DESCS[lvl - 1])

        if run_level(lvl):
            if lvl == 5:
                show_message("ПОБЕДА!", "Все курицы захвачены!", GLD)
                break
            else:
                show_message(f"Уровень {lvl} пройден!", "Курица захвачена!", GRN)
        else:
            show_message("GAME OVER", f"Уровень {lvl} — охрана победила.", RED)
            break
