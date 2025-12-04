import pygame, sys, math, random

# -----------------------------
# Configurazione iniziale
# -----------------------------
pygame.init()
WIDTH, HEIGHT = 700, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sci-Fi Pinball (Pivot Flippers)")
clock = pygame.time.Clock()

# Colori
BLACK=(10,10,18); WHITE=(240,240,240); BLUE=(0,160,255); CYAN=(0,220,220)
RED=(255,60,80); GREEN=(60,255,140); YELLOW=(255,220,70); MAGENTA=(255,80,200)
GRAY=(80,80,100)

# Font
font = pygame.font.SysFont("consolas", 24)
big_font = pygame.font.SysFont("consolas", 60)

# -----------------------------
# Parametri di gioco
# -----------------------------
gravity = 0.28
ball_radius = 10
ball_speed_init = 7
lives_init = 3
score = 0
lives = lives_init
target_score = 15000
game_state = "playing"

balls = []
max_active_balls = 6

walls = [
    pygame.Rect(0, 0, 12, HEIGHT),
    pygame.Rect(WIDTH-12, 0, 12, HEIGHT),
    pygame.Rect(0, 0, WIDTH, 12),
]
outlanes = [
    pygame.Rect(0, HEIGHT-220, 80, 220),
    pygame.Rect(WIDTH-80, HEIGHT-220, 80, 220)
]

bumpers = [
    {"pos": (WIDTH//2, HEIGHT//2-120), "r": 38, "color": CYAN, "label": "JACKPOT", "score": 1000},
    {"pos": (WIDTH//2-160, HEIGHT//2), "r": 28, "color": GREEN, "label": "BONUS", "score": 500},
    {"pos": (WIDTH//2+160, HEIGHT//2-30), "r": 28, "color": GREEN, "label": "BONUS", "score": 500},
]

combo_zones = [
    {"rect": pygame.Rect(WIDTH//2-220, 160, 120, 20), "color": MAGENTA, "label": "COMBO A", "lit": False},
    {"rect": pygame.Rect(WIDTH//2-60, 130, 120, 20), "color": YELLOW,  "label": "COMBO B", "lit": False},
    {"rect": pygame.Rect(WIDTH//2+100, 160, 120, 20), "color": BLUE,   "label": "COMBO C", "lit": False},
]
combo_timer_max = 5.0
combo_timer = 0.0
combo_sequence_index = 0

confetti = []
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(180)]

# -----------------------------
# Classe Flipper pivotato (rettangolo)
# -----------------------------
class Flipper:
    def __init__(self, pivot, length=150, thickness=20,
                 rest_deg=75, up_deg=20, side="left"):
        self.pivot = pygame.Vector2(pivot)
        self.length = length
        self.thickness = thickness
        self.side = side

        if side == "left":
            self.rest = math.radians(rest_deg)
            self.up = math.radians(up_deg)
        else:
            self.rest = math.radians(180 - rest_deg)
            self.up = math.radians(180 - up_deg)

        self.angle = self.rest
        self.angular_speed = math.radians(500)
        self.moving_up = False

    def update(self, dt, key_pressed):
        self.moving_up = key_pressed
        target = self.up if key_pressed else self.rest
        delta = target - self.angle
        max_step = self.angular_speed * dt
        if abs(delta) <= max_step:
            self.angle = target
        else:
            self.angle += max_step if delta > 0 else -max_step

    def tip_pos(self):
        dir_vec = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        return self.pivot + dir_vec * self.length

    def polygon(self):
        dir_vec = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        perp = dir_vec.rotate(90).normalize() * (self.thickness/2)
        a = self.pivot
        b = self.tip_pos()
        return [a+perp, b+perp, b-perp, a-perp]

    def draw(self, surf):
        pts = self.polygon()
        pygame.draw.polygon(surf, WHITE, [(p.x, p.y) for p in pts])
        pygame.draw.circle(surf, YELLOW, (int(self.pivot.x), int(self.pivot.y)), int(self.thickness*0.55))

    def collide_and_impulse(self, ball):
        pts = self.polygon()
        p = pygame.Vector2(ball["rect"].center)
        hit = False
        for i in range(len(pts)):
            a, b = pts[i], pts[(i+1)%len(pts)]
            ab = b - a
            ap = p - a
            seg_len2 = ab.length_squared()
            if seg_len2 == 0: continue
            t = max(0.0, min(1.0, ap.dot(ab)/seg_len2))
            closest = a + ab*t
            dist = (p-closest).length()
            if dist <= ball_radius:
                hit = True
                n = ab.rotate(90).normalize()
                v = pygame.Vector2(ball["vx"], ball["vy"])
                v_reflect = v - 2*v.dot(n)*n
                if self.moving_up:
                    v_reflect += pygame.Vector2(-3 if self.side=="left" else 3, -8)
                if v_reflect.length() < 6.5:
                    v_reflect.scale_to_length(6.5)
                ball["vx"], ball["vy"] = v_reflect.x, v_reflect.y
                ball["rect"].centerx += int(n.x*(ball_radius-dist))
                ball["rect"].centery += int(n.y*(ball_radius-dist))
                break
        return hit

# -----------------------------
# Istanze flipper
# -----------------------------
left_flipper = Flipper(pivot=(WIDTH//2 - 170, HEIGHT - 140), rest_deg=15, up_deg=0, side="left")
right_flipper = Flipper(pivot=(WIDTH//2 + 170, HEIGHT - 140), rest_deg=15, up_deg=0, side="right")

# -----------------------------
# Utility
# -----------------------------
def spawn_ball():
    if len(balls) >= max_active_balls:
        return
    x = WIDTH - 40  # plunger semplificato
    y = HEIGHT - 240
    angle = random.uniform(-2.60, -2.85)  # obliquo alto-sinistra
    vx = ball_speed_init * math.cos(angle)
    vy = ball_speed_init * math.sin(angle)
    rect = pygame.Rect(int(x - ball_radius), int(y - ball_radius), ball_radius*2, ball_radius*2)
    balls.append({"rect": rect, "vx": vx, "vy": vy})

def reset_game(full=True):
    global score, lives, game_state, balls, combo_timer, combo_sequence_index
    if full:
        score = 0
        lives = lives_init
        game_state = "playing"
    balls = []
    combo_timer = 0.0
    combo_sequence_index = 0
    for z in combo_zones:
        z["lit"] = False
    spawn_ball()

def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def bounce_off_bumper(ball, bx, by):
    cx = ball["rect"].centerx
    cy = ball["rect"].centery
    ang = math.atan2(cy - by, cx - bx)
    speed = max(6.0, math.hypot(ball["vx"], ball["vy"]))
    ball["vx"] = math.cos(ang) * speed * 1.05
    ball["vy"] = math.sin(ang) * speed * 1.05

def update_confetti():
    global confetti
    for c in confetti:
        c["vy"] += 0.08
        c["x"] += c["vx"]
        c["y"] += c["vy"]
    confetti = [c for c in confetti if c["y"] < HEIGHT + 40]

def start_confetti():
    global confetti
    confetti = []
    for _ in range(220):
        confetti.append({
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(-120, -20),
            "vx": random.uniform(-1.4, 1.4),
            "vy": random.uniform(1.0, 3.2),
            "color": random.choice([CYAN, MAGENTA, YELLOW, GREEN, BLUE, WHITE])
        })

# -----------------------------
# Logica combo e multiball
# -----------------------------
def handle_combo_collision(ball):
    global combo_sequence_index, combo_timer, score
    if combo_sequence_index >= len(combo_zones):
        return
    zone = combo_zones[combo_sequence_index]
    if zone["rect"].collidepoint(ball["rect"].centerx, ball["rect"].centery):
        zone["lit"] = True
        combo_sequence_index += 1
        score += 800
        combo_timer = combo_timer_max
        if combo_sequence_index == len(combo_zones):
            score += 3000
            spawn_ball()
            spawn_ball()

def update_combo_timer(dt):
    global combo_timer, combo_sequence_index
    if combo_sequence_index == 0:
        combo_timer = 0.0
        return
    combo_timer -= dt
    if combo_timer <= 0.0 and combo_sequence_index < len(combo_zones):
        combo_sequence_index = 0
        for z in combo_zones:
            z["lit"] = False
        combo_timer = 0.0

# -----------------------------
# Schermate di stato
# -----------------------------
def draw_game_over():
    screen.fill(BLACK)
    msg = big_font.render("GAME OVER", True, RED)
    tip = font.render("Premi R per ripartire", True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 80))
    screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT//2 + 10))

def draw_victory():
    screen.fill((12, 14, 30))
    update_confetti()
    for c in confetti:
        pygame.draw.rect(screen, c["color"], (int(c["x"]), int(c["y"]), 6, 10))
    msg = big_font.render("VICTORY!", True, YELLOW)
    tip = font.render("Hai vinto! Premi R per giocare ancora", True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 80))
    screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT//2 + 10))

# -----------------------------
# Avvio
# -----------------------------
reset_game(full=True)

# -----------------------------
# Loop principale
# -----------------------------
while True:
    dt = clock.tick(60) / 1000.0

    # Eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_SPACE:
                    spawn_ball()  # multiball test
            if event.key == pygame.K_r and game_state in ("gameover", "victory"):
                reset_game(full=True)
                confetti = []
                game_state = "playing"

    # Input flippers (← sinistra, → destra): ruotano verso l'alto
    keys = pygame.key.get_pressed()
    left_flipper.update(dt, key_pressed=keys[pygame.K_LEFT])
    right_flipper.update(dt, key_pressed=keys[pygame.K_RIGHT])

    # Logica di gioco
    if game_state == "playing":
        update_combo_timer(dt)

        # Aggiorna palline
        alive_balls = []
        for ball in balls:
            # gravità
            ball["vy"] += gravity
            # movimento
            ball["rect"].x += int(ball["vx"])
            ball["rect"].y += int(ball["vy"])

            cx, cy = ball["rect"].centerx, ball["rect"].centery

            # collisione bordi
            for w in walls:
                if w.collidepoint(cx, cy):
                    if w.left == 0: ball["vx"] = abs(ball["vx"])
                    if w.right == WIDTH: ball["vx"] = -abs(ball["vx"])
                    if w.top == 0: ball["vy"] = abs(ball["vy"])

            # collisione outlanes → pallina persa
            in_outlane = any(l.collidepoint(cx, cy) for l in outlanes)
            if in_outlane or ball["rect"].bottom >= HEIGHT:
                continue

            # collisione bumpers
            for bp in bumpers:
                bx, by = bp["pos"]
                r = bp["r"]
                if distance((cx, cy), (bx, by)) < (ball_radius + r):
                    bounce_off_bumper(ball, bx, by)
                    score += bp["score"]

            # collisione flippers con impulso
            hit_left = left_flipper.collide_and_impulse(ball)
            hit_right = right_flipper.collide_and_impulse(ball)
            if hit_left or hit_right:
                score += 30

            # combo zones
            handle_combo_collision(ball)

            alive_balls.append(ball)

        balls = alive_balls

        # Se non ci sono palline attive
        if len(balls) == 0:
            lives -= 1
            if lives <= 0:
                game_state = "gameover"
            else:
                spawn_ball()

        # Vittoria
        if score >= target_score:
            game_state = "victory"
            start_confetti()

    # -----------------------------
    # Disegno
    # -----------------------------
    if game_state == "playing":
        # sfondo
        screen.fill(BLACK)
        for sx, sy in stars:
            pygame.draw.circle(screen, WHITE, (sx, sy), 1)

        # campo e elementi
        for w in walls:
            pygame.draw.rect(screen, WHITE, w)
        for l in outlanes:
            pygame.draw.rect(screen, RED, l, 2)

        # bumpers
        for bp in bumpers:
            bx, by = bp["pos"]
            r = bp["r"]
            pygame.draw.circle(screen, bp["color"], (bx, by), r)
            lbl = font.render(bp["label"], True, WHITE)
            screen.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))

        # combo zones
        for i, z in enumerate(combo_zones):
            col = z["color"] if z["lit"] else GRAY
            pygame.draw.rect(screen, col, z["rect"])
            txt = font.render(z["label"], True, WHITE)
            screen.blit(txt, (z["rect"].centerx - txt.get_width()//2, z["rect"].y - 24))
        if combo_sequence_index > 0 and combo_sequence_index < len(combo_zones):
            timer_txt = font.render(f"Combo time: {combo_timer:.1f}s", True, YELLOW)
            screen.blit(timer_txt, (WIDTH//2 - timer_txt.get_width()//2, 100))

        # flippers pivot
        left_flipper.draw(screen)
        right_flipper.draw(screen)

        # palline
        for ball in balls:
            pygame.draw.circle(screen, BLUE, (ball["rect"].centerx, ball["rect"].centery), ball_radius)

        # HUD
        hud_score = font.render(f"Score: {score}", True, WHITE)
        hud_lives = font.render(f"Balls: {lives}", True, WHITE)
        hud_active = font.render(f"Active: {len(balls)}", True, WHITE)
        screen.blit(hud_score, (20, 20))
        screen.blit(hud_lives, (20, 50))
        screen.blit(hud_active, (20, 80))
        tip = font.render("← → flippers (ruotano verso l’alto) | SPACE multiball (test)", True, WHITE)
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, HEIGHT-40))

    elif game_state == "gameover":
        draw_game_over()

    elif game_state == "victory":
        draw_victory()

    pygame.display.flip()
