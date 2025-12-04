import pygame, sys, math, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flipper")

# Colori
BLACK=(0,0,0); WHITE=(255,255,255); RED=(255,0,0); BLUE=(0,149,221); GREEN=(0,255,0)

clock=pygame.time.Clock()
font=pygame.font.SysFont(None,36)

# Variabili di gioco
score=0
lives=3

# Pallina
ball_radius=10
ball=pygame.Rect(WIDTH//2, HEIGHT//2, ball_radius*2, ball_radius*2)
ball_dx, ball_dy = random.choice([-4,4]), -4

# Flippers
flipper_length=100
flipper_thickness=20
flipper_angle_left=30
flipper_angle_right=-30
flipper_speed=10

# Posizioni flipper
flipper_left_pos=(WIDTH//2-150, HEIGHT-100)
flipper_right_pos=(WIDTH//2+150, HEIGHT-100)

def draw_flipper(pos, angle, color):
    x,y=pos
    rect=pygame.Surface((flipper_length,flipper_thickness),pygame.SRCALPHA)
    rect.fill(color)
    rotated=pygame.transform.rotate(rect, angle)
    rect_center=(x,y)
    screen.blit(rotated, rotated.get_rect(center=rect_center))

def reset_ball():
    global ball, ball_dx, ball_dy
    ball=pygame.Rect(WIDTH//2, HEIGHT//2, ball_radius*2, ball_radius*2)
    ball_dx, ball_dy = random.choice([-4,4]), -4

# Loop principale
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT: pygame.quit(); sys.exit()

    keys=pygame.key.get_pressed()
    # Controllo flippers
    if keys[pygame.K_LEFT]:
        flipper_angle_left=min(flipper_angle_left+flipper_speed,60)
    else:
        flipper_angle_left=max(flipper_angle_left-5,30)

    if keys[pygame.K_RIGHT]:
        flipper_angle_right=max(flipper_angle_right-flipper_speed,-60)
    else:
        flipper_angle_right=min(flipper_angle_right+5,-30)

    # Movimento pallina
    ball.x+=ball_dx; ball.y+=ball_dy

    # Collisioni bordi
    if ball.left<=0 or ball.right>=WIDTH: ball_dx=-ball_dx
    if ball.top<=0: ball_dy=-ball_dy
    if ball.bottom>=HEIGHT:
        lives-=1
        if lives<=0:
            # Game Over
            screen.fill(BLACK)
            msg=font.render("GAME OVER - Premi R per ricominciare",True,RED)
            screen.blit(msg,(WIDTH//2-msg.get_width()//2,HEIGHT//2))
            pygame.display.flip()
            waiting=True
            while waiting:
                for e in pygame.event.get():
                    if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_r:
                        score=0; lives=3; reset_ball(); waiting=False
        else:
            reset_ball()

    # Collisione con flippers (semplificata: area rettangolare)
    flipper_left_rect=pygame.Rect(flipper_left_pos[0]-50, flipper_left_pos[1]-10, 100,20)
    flipper_right_rect=pygame.Rect(flipper_right_pos[0]-50, flipper_right_pos[1]-10, 100,20)
    if ball.colliderect(flipper_left_rect) or ball.colliderect(flipper_right_rect):
        ball_dy=-abs(ball_dy)
        score+=10

    # Disegno
    screen.fill(BLACK)
    pygame.draw.ellipse(screen, BLUE, ball)
    draw_flipper(flipper_left_pos, flipper_angle_left, WHITE)
    draw_flipper(flipper_right_pos, flipper_angle_right, WHITE)

    # HUD
    score_text=font.render(f"Score: {score}",True,WHITE)
    lives_text=font.render(f"Lives: {lives}",True,WHITE)
    screen.blit(score_text,(10,10))
    screen.blit(lives_text,(10,40))

    pygame.display.flip()
    clock.tick(60)
