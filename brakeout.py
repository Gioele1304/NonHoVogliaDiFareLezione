import pygame
import sys

# Inizializza pygame
pygame.init()

# Dimensioni finestra
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 149, 221)
RED = (255, 0, 0)

# Parametri
ball_radius = 10
paddle_width, paddle_height = 75, 10
paddle_speed = 10
brick_rows, brick_cols = 8, 10
brick_width, brick_height = 60, 20
brick_gap = 8

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)

# Variabili di gioco
score = 0
lives = 3
level = 1
ball_speed = 3
ball_active = False
last_direction = "right"  # per alternare direzioni

def reset_game():
    global ball, ball_dx, ball_dy, paddle, bricks, ball_active
    # Paddle
    paddle = pygame.Rect(WIDTH//2 - paddle_width//2, HEIGHT - 30, paddle_width, paddle_height)
    # Palla sopra la paletta
    ball = pygame.Rect(paddle.centerx - ball_radius, paddle.top - ball_radius*2, ball_radius*2, ball_radius*2)
    ball_dx, ball_dy = 0, 0
    ball_active = False
    # Mattoncini
    bricks = []
    total_bricks_width = brick_cols * brick_width + (brick_cols - 1) * brick_gap
    start_x = (WIDTH - total_bricks_width) // 2
    start_y = 50
    for row in range(brick_rows):
        for col in range(brick_cols):
            x = start_x + col * (brick_width + brick_gap)
            y = start_y + row * (brick_height + brick_gap)
            bricks.append(pygame.Rect(x, y, brick_width, brick_height))

def launch_ball():
    global ball_dx, ball_dy, ball_active, last_direction
    ball_active = True
    ball_dy = -ball_speed
    # Alterna direzione orizzontale
    if last_direction == "left":
        ball_dx = ball_speed
        last_direction = "right"
    else:
        ball_dx = -ball_speed
        last_direction = "left"

def game_over_menu():
    while True:
        screen.fill(BLACK)
        text1 = big_font.render("GAME OVER", True, WHITE)
        text2 = font.render("Q = Quit", True, RED)
        text3 = font.render("E = Restart", True, BLUE)

        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 80))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_e:
                    restart_game()
                    return

def restart_game():
    global score, lives, level, ball_speed
    score = 0
    lives = 3
    level = 1
    ball_speed = 3
    reset_game()

reset_game()  # 🔥 anche all'inizio la palla è sulla paletta

# Loop principale
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not ball_active:
                launch_ball()

    # Movimento paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-paddle_speed, 0)
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.move_ip(paddle_speed, 0)

    # Se la palla non è attiva, segue la paletta
    if not ball_active:
        ball.centerx = paddle.centerx
        ball.bottom = paddle.top

    # Movimento palla
    if ball_active:
        ball.move_ip(ball_dx, ball_dy)

        # Collisioni con bordi
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx = -ball_dx
        if ball.top <= 0:
            ball_dy = -ball_dy
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives <= 0:
                game_over_menu()
            else:
                reset_game()

        # Collisione con paddle
        if ball.colliderect(paddle):
            ball_dy = -abs(ball_dy)

        # Collisione con mattoncini (realistica)
        hit_index = ball.collidelist(bricks)
        if hit_index != -1:
            brick = bricks.pop(hit_index)

            overlap_left = ball.right - brick.left
            overlap_right = brick.right - ball.left
            overlap_top = ball.bottom - brick.top
            overlap_bottom = brick.bottom - ball.top

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                ball_dx = -abs(ball_dx)
            elif min_overlap == overlap_right:
                ball_dx = abs(ball_dx)
            elif min_overlap == overlap_top:
                ball_dy = -abs(ball_dy)
            elif min_overlap == overlap_bottom:
                ball_dy = abs(ball_dy)

            score += 10

        # Controllo fine livello
        if not bricks:
            level += 1
            ball_speed += 1
            reset_game()

    # Disegno
    screen.fill(BLACK)
    pygame.draw.ellipse(screen, BLUE, ball)
    pygame.draw.rect(screen, WHITE, paddle)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    # HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(level_text, (10, 70))

    # Messaggio se la palla è ferma
    if not ball_active:
        msg = font.render("Premi SPAZIO per lanciare", True, BLUE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)
