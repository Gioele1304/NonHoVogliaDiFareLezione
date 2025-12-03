import pygame
import sys

level=0

pygame.init()

# Finestra
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Simplified")

# Colori
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED   = (255,0,0)

font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# Player
player_w, player_h = 50, 10
player = pygame.Rect(WIDTH//2 - player_w//2, HEIGHT-40, player_w, player_h)
player_speed = 6

# Bullet
bullet_w, bullet_h = 4, 10
bullets = []

# Enemy
enemy_w, enemy_h = 40, 20
def spawn_enemies(rows=3, cols=8):
    enemies = []
    for r in range(rows):
        for c in range(cols):
            x = c*70+20
            y = r*50+20
            enemies.append(pygame.Rect(x,y,enemy_w,enemy_h))
    return enemies

enemies = spawn_enemies()
enemy_speed = 1
enemy_dir = 1

# Punteggio e vite
score = 0
lives = 3
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bullets.append(pygame.Rect(player.centerx - bullet_w//2, player.top, bullet_w, bullet_h))

    keys = pygame.key.get_pressed()
    if not game_over:
        # Movimento player
        if keys[pygame.K_LEFT] and player.left > 0:
            player.move_ip(-player_speed, 0)
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.move_ip(player_speed, 0)

        # Movimento enemies
        for e in enemies:
            e.move_ip(enemy_speed*enemy_dir, 0)
        min_left = min(e.left for e in enemies)
        max_right = max(e.right for e in enemies)
        if max_right >= WIDTH or min_left <= 0:
            enemy_dir *= -1
            for e in enemies:
                e.move_ip(0, 30)

        # Movimento bullets
        for b in bullets[:]:
            b.move_ip(0, -6)
            if b.bottom < 0:
                bullets.remove(b)

        # Collisioni bullets-enemies
        for b in bullets[:]:
            hit = b.collidelist(enemies)
            if hit != -1:
                enemies.pop(hit)
                bullets.remove(b)
                score += 10

        # 🔥 Controllo vite e game over
        for e in enemies:
            if e.bottom >= player.top:
                lives -= 1
                enemies = spawn_enemies()  # nuova ondata
                bullets.clear()
                enemy_speed = enemy_speed
                enemy_dir = enemy_dir
                if lives <= 0:
                    game_over = True
                break

        # Respawn infinito
        if not enemies and not game_over:
            enemy_speed += 0.5
            enemy_dir = 1
            enemies = spawn_enemies()
            level+=1

    # Disegno
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREEN, player)
    for b in bullets:
        pygame.draw.rect(screen, WHITE, b)
    for e in enemies:
        pygame.draw.rect(screen, RED, e)

    score_text = font.render(f"Score: {score}", True, (0, 255, 0))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 0))
    levels_text = font.render(f"Level: {level}", True, (255, 148, 250))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(levels_text, (10, 70))

    if game_over:
        msg = font.render(f"GAME OVER - Score: {score}", True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
        level=0

    pygame.display.flip()
    clock.tick(60)
