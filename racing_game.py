import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("公路飙车")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
RED = (220, 40, 40)
YELLOW = (255, 220, 0)
GREEN = (40, 200, 40)
ORANGE = (255, 140, 0)
BLUE = (40, 120, 255)
ROAD_COLOR = (50, 50, 50)
GRASS_COLOR = (30, 100, 30)

ROAD_LEFT = 60
ROAD_RIGHT = 440
LANE_COUNT = 4
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT

font_small = pygame.font.Font(None, 30)
font_medium = pygame.font.Font(None, 50)
font_large = pygame.font.Font(None, 70)
font_title = pygame.font.Font(None, 60)

best_score = 0
best_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "racing_best.txt")
try:
    with open(best_file, "r") as f:
        best_score = int(f.read().strip())
except:
    pass

player_colors = [(220, 40, 40), (40, 120, 255), (255, 140, 0), (40, 200, 40), (220, 40, 200), (40, 220, 220)]
enemy_color_sets = [
    [(255, 255, 50), (50, 50, 50)],
    [(255, 100, 100), (30, 30, 30)],
    [(100, 100, 255), (20, 20, 20)],
    [(255, 160, 50), (40, 40, 40)],
    [(160, 50, 255), (30, 30, 30)],
    [(50, 200, 200), (20, 20, 20)],
]

car_width, car_height = 55, 90


def draw_car(surf, x, y, body_color, dark_color=(30, 30, 30), player=False):
    cx, cy = int(x), int(y)
    bw, bh = car_width, car_height

    rect = pygame.Rect(cx - bw // 2 + 4, cy - bh // 2 + 8, bw - 8, bh - 16)
    pygame.draw.rect(surf, body_color, rect, border_radius=6)

    top_rect = pygame.Rect(cx - bw // 2 + 10, cy - bh // 2 + 4, bw - 20, bh - 30)
    pygame.draw.rect(surf, dark_color, top_rect, border_radius=4)

    if player:
        wc = (180, 220, 255)
    else:
        wc = (80, 80, 100)
    win_rect = pygame.Rect(cx - bw // 2 + 13, cy - bh // 2 + 8, bw - 26, 18)
    pygame.draw.rect(surf, wc, win_rect, border_radius=3)

    rear_rect = pygame.Rect(cx - bw // 2 + 13, cy - bh // 2 + bh - 34, bw - 26, 14)
    pygame.draw.rect(surf, wc, rear_rect, border_radius=3)

    wheel_w, wheel_h = 9, 18
    for wx in [cx - bw // 2 - 2, cx + bw // 2 - wheel_w + 2]:
        for wy in [cy - bh // 2 + 12, cy + bh // 2 - wheel_h - 12]:
            pygame.draw.rect(surf, (20, 20, 20), (wx, wy, wheel_w, wheel_h), border_radius=2)

    hl_size = 5
    for hx in [cx - 14, cx + 14 - hl_size]:
        pygame.draw.rect(surf, YELLOW, (hx, cy - bh // 2 - 1, hl_size, hl_size), border_radius=2)

    tl_size = 5
    for tx in [cx - 14, cx + 14 - tl_size]:
        pygame.draw.rect(surf, RED, (tx, cy + bh // 2 - tl_size + 1, tl_size, tl_size), border_radius=2)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 120
        self.speed = 6
        self.color = random.choice(player_colors)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if self.x < ROAD_LEFT + car_width // 2:
            self.x = ROAD_LEFT + car_width // 2
        if self.x > ROAD_RIGHT - car_width // 2:
            self.x = ROAD_RIGHT - car_width // 2

    def draw(self, surf):
        draw_car(surf, self.x, self.y, self.color, player=True)

    def rect(self):
        return pygame.Rect(self.x - car_width // 2 + 4, self.y - car_height // 2 + 4, car_width - 8, car_height - 8)


class Enemy:
    def __init__(self, speed):
        self.x = random.randint(ROAD_LEFT + car_width // 2, ROAD_RIGHT - car_width // 2)
        self.y = -car_height
        self.speed = speed
        colors = random.choice(enemy_color_sets)
        self.body_color = colors[0]
        self.dark_color = colors[1]

    def update(self):
        self.y += self.speed

    def draw(self, surf):
        draw_car(surf, self.x, self.y, self.body_color, self.dark_color)

    def rect(self):
        return pygame.Rect(self.x - car_width // 2 + 4, self.y - car_height // 2 + 4, car_width - 8, car_height - 8)

    def off_screen(self):
        return self.y > HEIGHT + car_height


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.max_life = 30
        self.color = random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        radius = int(4 * alpha)
        if radius > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), radius)

    def dead(self):
        return self.life <= 0


def spawn_particles(x, y, count=15):
    return [Particle(x, y) for _ in range(count)]


def draw_road(surf, offset):
    pygame.draw.rect(surf, GRASS_COLOR, (0, 0, ROAD_LEFT, HEIGHT))
    pygame.draw.rect(surf, GRASS_COLOR, (ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT))
    pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.rect(surf, WHITE, (ROAD_LEFT - 4, 0, 6, HEIGHT))
    pygame.draw.rect(surf, WHITE, (ROAD_RIGHT - 2, 0, 6, HEIGHT))

    dash_h = 40
    gap = 30
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        start_y = -(offset % (dash_h + gap))
        y = start_y
        while y < HEIGHT:
            pygame.draw.rect(surf, WHITE, (lx - 2, y, 4, dash_h))
            y += dash_h + gap


def game_over_screen(scr, is_new_best, total_score=0, best=0):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.set_alpha(180)
    fade.fill(BLACK)
    screen.blit(fade, (0, 0))

    if is_new_best:
        title = font_large.render("新纪录!", True, YELLOW)
    else:
        title = font_large.render("游戏结束", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

    score_txt = font_medium.render(f"得分: {scr}", True, WHITE)
    screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 250))

    best_txt = font_small.render(f"最高分: {best}", True, GRAY)
    screen.blit(best_txt, (WIDTH // 2 - best_txt.get_width() // 2, 310))

    hint1 = font_small.render("按 SPACE 重新开始", True, GREEN)
    screen.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 400))

    hint2 = font_small.render("按 ESC 退出游戏", True, RED)
    screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 440))


def start_screen():
    while True:
        screen.fill(BLACK)
        draw_road(screen, 0)

        title = font_title.render("公路飙车", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))

        info1 = font_small.render("← → 或 A / D 控制方向", True, WHITE)
        screen.blit(info1, (WIDTH // 2 - info1.get_width() // 2, 300))

        info2 = font_small.render("躲避来车，坚持越久分数越高", True, GRAY)
        screen.blit(info2, (WIDTH // 2 - info2.get_width() // 2, 340))

        start_txt = font_medium.render("按 SPACE 开始", True, GREEN)
        screen.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 420))

        best_txt = font_small.render(f"最高分: {best_score}", True, ORANGE)
        screen.blit(best_txt, (WIDTH // 2 - best_txt.get_width() // 2, 480))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        clock.tick(60)


def main():
    global best_score

    start_screen()

    player = Player()
    enemies = []
    particles = []
    score = 0
    road_offset = 0
    spawn_timer = 0
    base_speed = 4
    running = True
    game_over = False
    total_score = 0

    while running:
        dt = clock.tick(60)
        road_offset = (road_offset + 4) % 10000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if not game_over:
            player.update(keys)
            enemy_speed = base_speed + score // 200

            spawn_interval = max(25, 55 - score // 150)
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                if random.random() < 0.75:
                    enemies.append(Enemy(enemy_speed))

            for enemy in enemies[:]:
                enemy.update()
                if enemy.off_screen():
                    enemies.remove(enemy)
                    score += 5

            for enemy in enemies:
                if player.rect().colliderect(enemy.rect()):
                    game_over = True
                    total_score = score
                    particles += spawn_particles(player.x, player.y, 40)
                    if score > best_score:
                        best_score = score
                        try:
                            with open(best_file, "w") as f:
                                f.write(str(best_score))
                        except:
                            pass
                    break

            score += 1

        for p in particles[:]:
            p.update()
            if p.dead():
                particles.remove(p)

        screen.fill(BLACK)
        draw_road(screen, road_offset)

        for enemy in enemies:
            enemy.draw(screen)

        if not game_over:
            player.draw(screen)

        for p in particles:
            p.draw(screen)

        score_txt = font_medium.render(f"{score}", True, WHITE)
        screen.blit(score_txt, (WIDTH - score_txt.get_width() - 20, 20))

        spd_label = font_small.render("SPEED", True, GRAY)
        screen.blit(spd_label, (20, 18))
        spd = base_speed + score // 200
        spd_color = GREEN if spd < 8 else (YELLOW if spd < 12 else RED)
        spd_txt = font_medium.render(f"{int(spd * 20)}", True, spd_color)
        screen.blit(spd_txt, (20, 40))

        if game_over:
            is_new = total_score >= best_score and total_score > 0
            game_over_screen(total_score, is_new, total_score, best_score)
            if keys[pygame.K_SPACE]:
                player = Player()
                enemies = []
                particles = []
                score = 0
                spawn_timer = 0
                game_over = False
            if keys[pygame.K_ESCAPE]:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
